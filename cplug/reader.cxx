# include <Python.h>
# include <fstream>
# include <string>
# include <iostream>
using namespace std;

string concatinate(string first, string second) { 
    string endline = "\n";
    return first + endline + second;
}

string Cread(const char* filename) {
    ifstream file(filename);
    string line, lines;

    if (file.is_open()) {
        while (getline(file, line)) {
            lines = concatinate(lines, line);
        }
    } else {
        lines = "bad open";
    }
    file.close();
    return lines;
}

static PyObject* read(PyObject *self, PyObject *args) {
    PyObject* filename_obj;

    if (!PyArg_ParseTuple(args, "U", &filename_obj)) {
        return NULL;
    }

    const char* filename = PyUnicode_AsUTF8(filename_obj);
    string read_result = Cread(filename);

    return PyUnicode_FromString(read_result.c_str());
}

static PyMethodDef methods[] = {
    {"read", read, METH_VARARGS, "C reading files"},
    {NULL, NULL, 0, NULL} 
};

static struct PyModuleDef module = {
    PyModuleDef_HEAD_INIT,
    "reader",
    "Reader",
    -1,
    methods
};

PyMODINIT_FUNC PyInit_reader(void) {
    return PyModule_Create(&module);
}