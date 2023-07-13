# include <Python.h>
# include <stdio.h>
# include <stdlib.h>
# include <fstream>
# include <iostream>
# include <string>
# include <ctime>
using namespace std;

string get_ascii_list() {
	string ascii_letters = "";
	for (int i = 65; i < 90; i++) {
		string ascii_char = static_cast<char>(i);
		ascii_letters += ascii_char;
	}
	for (int i = 97; i < 122; i++) {
		string ascii_char = static_cast<char>(i);
		ascii_letters += ascii_char;
	}
	for (int i = 0; i < 10; i++) {
		ascii_letters += to_string(i);
	}

	return ascii_letters;
}

string get_ascii_uppercase() {
	string ascii_letters = "";
	for (int i = 65; i < 90; i++) {
		string ascii_char = static_cast<char>(i);
		ascii_letters += ascii_char;
	}

	return ascii_letters;
}

void init_random() {
	srand(time(NULL));
}

int randint(int range_min, int range_max) {
    return ((double)rand() / RAND_MAX) * (range_max - range_min) + range_min;
}

string concatinate(string first, string second) {
    string endline = "\n";
    return first + endline + second;
}

string read(const char* filename) {
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

int write(const char* filename, const char* lines) {
    FILE* fm = fopen(filename, "wt");

    if (fm == NULL) {

        return 0;
    } else {

        fprintf(fm, "%s", lines);
        fclose(fm);

        return 1;
    }
}

bool exists(char* filename) {
    ifstream file(filename);
    return file.good();
}

static PyObject* init(PyObject *self, PyObject *args) {
	init_random();
	if (!exists("cache/forms.json")) {
		write("cache/forms.json", "{}");
	} if (!exists("cache/off.pylist")) {
		write("cache/off.pylist", "[]");
	} if (!exists("cache/no_registred.pylist")) {
		write("cache/no_registred.pylist", "[]");
	} if (!exists("cache/time_database.toml")) {
		write("cache/time_database.toml", "[test]\n3=[]\n5=[]\nweek=[]\nmonth=[]\n");
	} if (!exists("cache/rates.txt")) {
		write("cache/rates.txt", "");
	} if (!exists("cache/promo.pylist")) {
		write("cache/promo.pylist", "[]");
	} if (!exists("cache/aipu.pylist")) {
		write("cache/aipu.pylist", "[]");
	}

	return Py_None;
}

static PyObject* get_key(PyObject* self, PyObject* args) {
	string random_key = "";
	string ascii_list = get_ascii_list();

	for (int i = 0; i < randint(10, 100); i++) {
		random_key += ascii_list[randint(0, ascii_list.length())];
	}

	return PyUnicode_FromString(random_key.c_str());
}

static PyObject* gen_promo(PyObject* self, PyObject* args) {
	string uppercase = get_ascii_uppercase();
	string promocode = uppercase[randint(0, uppercase.length())] + to_string(randint(100, 999));

	return PyUnicode_FromString(promocode.c_str());
}
