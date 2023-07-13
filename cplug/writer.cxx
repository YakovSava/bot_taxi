# include <Python.h>
# include <stdio.h>
# include <iostream>
using namespace std;

int Cwrite(const char* filename, const char* lines) {
    FILE* fm = fopen(filename, "wt");

    if (fm == NULL) {

        return 0;
    } else {

        fprintf(fm, "%s", lines);
        fclose(fm);

        return 1;
    }
}

static PyObject* write(PyObject *self, PyObject *args) {
    PyObject *filename_obj, *data_obj;

    if (!PyArg_ParseTuple(args, "UU", &filename_obj, &data_obj)) {
        return NULL;
    }

    const char *filename = PyUnicode_AsUTF8(filename_obj);
    const char *data = PyUnicode_AsUTF8(data_obj);

    Cwrite(filename, data);

    return Py_None;
}

static PyMethodDef methods[] = {
    {"write", write, METH_VARARGS, "C writing to file"},
    {NULL, NULL, 0, NULL} 
};

static struct PyModuleDef module = {
    PyModuleDef_HEAD_INIT,
    "writer",
    "Writer",
    -1,
    methods
};

PyMODINIT_FUNC PyInit_writer(void) {
    return PyModule_Create(&module);
}