#include <string.h>     // memset

PyMODINIT_FUNC PyInit_examplemodule(void);

static PyModuleDef module_def_and_token;

PyMODINIT_FUNC
PyInit_examplemodule(void)
{
    PyModuleDef_Slot *slot = PyModExport_examplemodule();

    if (module_def_and_token.m_name) {
        // Take care to only set up the static PyModuleDef once.
        // (PyModExport might theoretically return different data each time.)
        return PyModuleDef_Init(&module_def_and_token);
    }
    int copying_slots = 1;
    for (/* slot set above */; slot->slot; slot++) {
        switch (slot->slot) {
        // Set PyModuleDef members from slots. These slots must come first.
#       define COPYSLOT_CASE(SLOT, MEMBER, TYPE)                            \
            case SLOT:                                                      \
                if (!copying_slots) {                                       \
                    PyErr_SetString(PyExc_SystemError,                      \
                                    #SLOT " must be specified earlier");    \
                    goto error;                                             \
                }                                                           \
                module_def_and_token.MEMBER = (TYPE)(slot->value);          \
                break;                                                      \
            /////////////////////////////////////////////////////////////////
        COPYSLOT_CASE(Py_mod_name, m_name, char*)
        COPYSLOT_CASE(Py_mod_doc, m_doc, char*)
        COPYSLOT_CASE(Py_mod_state_size, m_size, Py_ssize_t)
        COPYSLOT_CASE(Py_mod_methods, m_methods, PyMethodDef*)
        COPYSLOT_CASE(Py_mod_state_traverse, m_traverse, traverseproc)
        COPYSLOT_CASE(Py_mod_state_clear, m_clear, inquiry)
        COPYSLOT_CASE(Py_mod_state_free, m_free, freefunc)
        case Py_mod_token:
            // With PyInit_, the PyModuleDef is used as the token.
            if (slot->value != &module_def_and_token) {
                PyErr_SetString(PyExc_SystemError,
                                "Py_mod_token must be set to "
                                "&module_def_and_token");
                goto error;
            }
            break;
        default:
            // The remaining slots become m_slots in the def.
            // (`slot` now points to the "rest" of the original
            //  zero-terminated array.)
            if (copying_slots) {
                module_def_and_token.m_slots = slot;
            }
            copying_slots = 0;
            break;
        }
    }
    if (!module_def_and_token.m_name) {
        // This function needs m_name as the "is initialized" marker.
        PyErr_SetString(PyExc_SystemError, "Py_mod_name slot is required");
        goto error;
    }
    return PyModuleDef_Init(&module_def_and_token);

error:
    memset(&module_def_and_token, 0, sizeof(module_def_and_token));
    return NULL;
}
