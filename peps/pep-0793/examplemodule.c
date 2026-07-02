/*
Example module with C-level module-global state, and

- a simple function that updates and queries the state
- a class wihose repr() queries the same module state (as an example of
  PyType_GetModuleByToken)

Once compiled and renamed to not include a version tag (for example
examplemodule.so on Linux), this will run succesfully on both regular
and free-threaded builds.

Python usage:

import examplemodule
print(examplemodule.increment_value())  # 0
print(examplemodule.increment_value())  # 1
print(examplemodule.increment_value())  # 2
print(examplemodule.increment_value())  # 3


class Subclass(examplemodule.ExampleType):
    pass

instance = Subclass()
print(instance)  # <Subclass object; module value = 3>

*/

// Avoid CPython-version-specific ABI (inline functions & macros):
#define Py_LIMITED_API 0x030f0000  // 3.15

#include <Python.h>

typedef struct {
    int value;
} examplemodule_state;

static PySlot examplemodule_slots[];

#ifndef MOD_TOKEN
// Module token: normally set to the slots array,
// but a backwards-compatibility shim will redefine it.
#define MOD_TOKEN (&examplemodule_slots)
#endif

// increment_value function

static PyObject *
increment_value(PyObject *module, PyObject *_ignored)
{
    examplemodule_state *state = PyModule_GetState(module);
    int result = ++(state->value);
    return PyLong_FromLong(result);
}

static PyMethodDef examplemodule_methods[] = {
    {"increment_value", increment_value, METH_NOARGS},
    {NULL}
};

// ExampleType

static PyObject *
exampletype_repr(PyObject *self)
{
    /* To get module state, we cannot use PyModule_GetState(Py_TYPE(self)),
     * since Py_TYPE(self) might be a subclass defined in an unrelated module.
     * So, we should use use PyType_GetModuleByToken.
     * For pre-3.15 compatibility, we use PyType_GetModuleByDef instead:
     * this needs a cast and returns a borrowed reference.
     */
    PyObject *module = PyType_GetModuleByDef(
        Py_TYPE(self), (PyModuleDef*)MOD_TOKEN);
    if (!module) {
        return NULL;
    }
    examplemodule_state *state = PyModule_GetState(module);
    if (!state) {
        return NULL;
    }
    return PyUnicode_FromFormat("<ExampleType object; module value = %d>",
                                state->value);
}

static PyType_Spec exampletype_spec = {
    .name = "examplemodule.ExampleType",
    .flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .slots = (PyType_Slot[]) {
        {Py_tp_repr, exampletype_repr},
        {0},
    },
};

// Module

static int
examplemodule_exec(PyObject *module) {
    examplemodule_state *state = PyModule_GetState(module);
    state->value = -1;
    PyTypeObject *type = (PyTypeObject*)PyType_FromModuleAndSpec(
        module, &exampletype_spec, NULL);
    if (!type) {
        return -1;
    }
    if (PyModule_AddType(module, type) < 0) {
        Py_DECREF(type);
        return -1;
    }
    Py_DECREF(type);
    return 0;
}

PyDoc_STRVAR(examplemodule_doc, "Example extension.");

PyABIInfo_VAR(abi_info);

static PySlot examplemodule_slots[] = {
    PySlot_STATIC_DATA(Py_mod_abi, &abi_info),
    PySlot_STATIC_DATA(Py_mod_name, "examplemodule"),
    PySlot_STATIC_DATA(Py_mod_doc, (char*)examplemodule_doc),
    PySlot_STATIC_DATA(Py_mod_methods, examplemodule_methods),
    PySlot_SIZE(Py_mod_state_size, sizeof(examplemodule_state)),
    PySlot_FUNC(Py_mod_exec, examplemodule_exec),
    PySlot_STATIC_DATA(Py_mod_token, MOD_TOKEN),
    PySlot_END
};

// Avoid "implicit declaration of function" warning:
PyMODEXPORT_FUNC PyModExport_examplemodule(void);

PyMODEXPORT_FUNC
PyModExport_examplemodule(void)
{
    return examplemodule_slots;
}
