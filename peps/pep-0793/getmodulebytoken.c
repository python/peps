#include <Python.h>

typedef struct {
    PyObject *exception;
    PyTypeObject *type;
} SpamState;

static const PyModuleDef_Slot spam_slots[];

/// example-start
static PyObject *
spamtype_raise_exc(PyObject *self, PyObject *unused)
{
    PyObject *module = PyType_GetModuleByToken(Py_TYPE(self), spam_slots);
    if (!module) {
        return NULL;
    }
    SpamState *state = PyModule_GetState(module);
    if (!state) {
        return NULL;
    }
    PyErr_SetString(state->exception, "failed!");
    return NULL;
}
/// example-end

static PyType_Spec spamtype_spec = {
    .name = "spam.SpamType",
    .flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .slots = (PyType_Slot[]) {
        {
            Py_tp_methods,
            (PyMethodDef[]) {
                {"raise_exc", spamtype_raise_exc, METH_NOARGS},
                {0},
            }
        },
        {0},
    },
};

static int
spam_exec(PyObject *self)
{
    SpamState *state = PyModule_GetState(self);
    state->exception = PyErr_NewException("spam.SpamException", NULL, NULL);
    if (!state->exception) {
        return -1;
    }
    state->type = (PyTypeObject*)PyType_FromModuleAndSpec(self, &spamtype_spec, NULL);
    if (!state->type) {
        return -1;
    }
    if (PyModule_AddType(self, state->type) < 0) {
        return -1;
    }
    return 0;
}

static int
spam_traverse(PyObject *self, visitproc visit, void *arg)
{
    SpamState *state = PyModule_GetState(self);
    Py_VISIT(state->exception);
    Py_VISIT(state->type);
    return 0;
}

static int
spam_clear(PyObject *self)
{
    SpamState *state = PyModule_GetState(self);
    Py_CLEAR(state->exception);
    Py_CLEAR(state->type);
    return 0;
}

static void
spam_free(PyObject *self)
{
    spam_clear(self);
}

static const PyModuleDef_Slot spam_slots[] = {
    {Py_mod_exec, spam_exec},
    {Py_mod_state_size, (void*)sizeof(SpamState)},
    {Py_mod_state_traverse, spam_traverse},
    {Py_mod_state_clear, spam_clear},
    {Py_mod_state_free, spam_free},
    {0},
};

PyMODEXPORT_FUNC
PyModExport_spam(void)
{
    return spam_slots;
}
