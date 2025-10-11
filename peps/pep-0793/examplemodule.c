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

static PyModuleDef_Slot examplemodule_slots[];

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
     * So, use PyType_GetModuleByToken.
     */
    PyObject *module = PyType_GetModuleByToken(
        Py_TYPE(self), examplemodule_slots);
    if (!module) {
        return NULL;
    }
    examplemodule_state *state = PyModule_GetState(module);
    Py_DECREF(module);
    if (!state) {
        return NULL;
    }
    return PyUnicode_FromFormat("<%T object; module value = %d>",
                                self, state->value);
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

static PyModuleDef_Slot examplemodule_slots[] = {
    {Py_mod_name, "examplemodule"},
    {Py_mod_doc, (char*)examplemodule_doc},
    {Py_mod_methods, examplemodule_methods},
    {Py_mod_state_size, (void*)sizeof(examplemodule_state)},
    {Py_mod_exec, (void*)examplemodule_exec},
    {0}
};

// Avoid "implicit declaration of function" warning:
PyMODEXPORT_FUNC PyModExport_examplemodule(void);

PyMODEXPORT_FUNC
PyModExport_examplemodule(void)
{
    return examplemodule_slots;
}
