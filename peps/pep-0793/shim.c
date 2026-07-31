#include <Python.h>

// Hack: Restore old definition of Py_TYPE
#undef Py_TYPE
#define Py_TYPE(OBJ) (((PyObject*)OBJ)->ob_type)

// PyModuleDef, also reused as module token
static PyModuleDef module_def_and_token;
#define MOD_TOKEN (&module_def_and_token)

#include "examplemodule.c"

extern PySlot *PyModExport_examplemodule(void);

PyMODINIT_FUNC PyInit_examplemodule(void);

PyMODINIT_FUNC
PyInit_examplemodule(void)
{
    if (module_def_and_token.m_name) {
        // Take care to only set up the static PyModuleDef once.
        // (PyModExport might theoretically return different data each time.)
        return PyModuleDef_Init(&module_def_and_token);
    }

    static PyModuleDef_Slot module_slots[5] = {{0}};
    module_def_and_token.m_slots = module_slots;
    int current_m_slot = 0;

    PySlot *slot = PyModExport_examplemodule();

    for (/* slot set above */; slot->sl_id; slot++) {
        switch (slot->sl_id) {
        // Set PyModuleDef members from slots. These slots must come first.
#       define COPYSLOT_CASE(SLOT, DEF_MEMBER, SL_MEMBER, TYPE)               \
            case SLOT:                                                        \
                if (slot->sl_flags & PySlot_INTPTR) {                         \
                    module_def_and_token.DEF_MEMBER = (TYPE)(slot->sl_ptr);   \
                } else {                                                      \
                    module_def_and_token.DEF_MEMBER = (TYPE)(slot->SL_MEMBER);\
                }                                                             \
                break;                                                        \
            ///////////////////////////////////////////////////////////////////
        COPYSLOT_CASE(Py_mod_name, m_name, sl_ptr, char*)
        COPYSLOT_CASE(Py_mod_doc, m_doc, sl_ptr, char*)
        COPYSLOT_CASE(Py_mod_state_size, m_size, sl_size, Py_ssize_t)
        COPYSLOT_CASE(Py_mod_methods, m_methods, sl_ptr, PyMethodDef*)
        COPYSLOT_CASE(Py_mod_state_traverse, m_traverse, sl_func, traverseproc)
        COPYSLOT_CASE(Py_mod_state_clear, m_clear, sl_func, inquiry)
        COPYSLOT_CASE(Py_mod_state_free, m_free, sl_func, freefunc)
        COPYSLOT_CASE(Py_mod_slots, m_slots, sl_ptr, PyModuleDef_Slot*)
#       undef COPYSLOT_CASE
        case Py_mod_create:
        case Py_mod_exec:
        case Py_mod_multiple_interpreters:
        case Py_mod_gil:
            int old_slot_id = (int)slot->sl_id;
            if (old_slot_id > 83) {
                // Hack: slots were renumbered; use old IDs here
                old_slot_id -= 83;
            }
            module_slots[current_m_slot].slot = old_slot_id;
            module_slots[current_m_slot].value = slot->sl_ptr;
            current_m_slot++;
            if (current_m_slot >= 4) {
                PyErr_SetString(PyExc_SystemError,
                                "Too many slots for array");
                goto error;
            }
            break;
        case Py_mod_token:
            // With PyInit_, the PyModuleDef is used as the token.
            if (slot->sl_ptr != &module_def_and_token) {
                PyErr_SetString(PyExc_SystemError,
                                "Py_mod_token must be set to "
                                "&module_def_and_token");
                goto error;
            }
            break;
        case Py_mod_abi:
            // ABI checking skipped here
            break;
        default:
            if (!(slot->sl_flags & PySlot_OPTIONAL)) {
                PyErr_Format(PyExc_SystemError,
                             "Unknown slot ID %d.", (int)slot->sl_id);
                goto error;
            }
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
    module_def_and_token.m_name = NULL;
    return NULL;
}
