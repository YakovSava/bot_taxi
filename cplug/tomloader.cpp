# include <Python.h>
# include "tomloader.hpp"

static PyObject* toml_is_correct(PyObject *self, PyObject *args) {
    PyObject* filename_obj;

    if (!PyArg_ParseTuple(args, "U", &filename_obj)) {
        return NULL;
    }

    const char* filename = PyUnicode_AsUTF8(filename_obj);
    bool correct = toml_iscorrect(filename);

    return Py_BuildValue("i", correct ? 1 : 0);
}

static PyObject* toml_protect(PyObject *self, PyObject *args) {
    PyObject* filename_obj;

    if (!PyArg_ParseTuple(args, "U", &filename_obj)) {
        return NULL;
    }

    const char* filename = PyUnicode_AsUTF8(filename_obj);
    toml_protector(filename);

    return Py_None;
}

static PyMethodDef methods[] = {
    {"toml_is_correct", toml_is_correct, METH_VARARGS, "Check toml, if toml not correct return False"},
    {"toml_protect", toml_protect, METH_VARARGS, "Toml protector writing in C++"},
    {NULL, NULL, 0, NULL} 
};

static struct PyModuleDef module = {
    PyModuleDef_HEAD_INIT,
    "tomloader",
    "Tomloader",
    -1,
    methods
};

PyMODINIT_FUNC PyInit_tomloader(void) {
    return PyModule_Create(&module);
}