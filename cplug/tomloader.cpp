# include <Python.h>
# include "tomloader.hpp"

static PyObject* toml_protect(PyObject *self, PyObject *args) {
    PyObject* filename_obj;

    if (!PyArg_ParseTuple(args, "U", &filename_obj)) {
        return NULL;
    }

    const char* filename = PyUnicode_AsUTF8(filename_obj);
    toml_protector(filename);

    return PyNone;
}

static PyObject* toml_is_correct(PyObject *self, PyObject *args) {
    PyObject* filename_obj;

    if (!PyArg_ParseTuple(args, "U", &filename_obj)) {
        return NULL;
    }

    const char* filename = PyUnicode_AsUTF8(filename_obj);
    toml_protector(filename);

    return PyNone;
}