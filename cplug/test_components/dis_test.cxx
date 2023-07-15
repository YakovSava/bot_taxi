# include <stdio.h>
# include <stdlib.h>
# include <fstream>
# include <iostream>
# include <string>
# include <ctime>
using namespace std;

string char_to_string(char ch) {
    string str(1, ch);
    return str;
}

string get_ascii_list() {
    string ascii_letters;
    for (int i = 65; i < 90; i++) {
        ascii_letters += char_to_string(static_cast<char>(i));
    }
    for (int i = 97; i < 122; i++) {
        ascii_letters += char_to_string(static_cast<char>(i));
    }
    for (int i = 0; i < 10; i++) {
        ascii_letters += to_string(i);
    }

    cout << ascii_letters << endl;
    return ascii_letters;
}

string get_ascii_uppercase() {
	string ascii_letters = "";
	for (int i = 65; i < 90; i++) {
		string ascii_char = char_to_string(static_cast<char>(i));
		ascii_letters += ascii_char;
	}

	return ascii_letters;
}

int randint(int range_min, int range_max) {
	return ((double)rand() / RAND_MAX) * (range_max - range_min) + range_min;
}

void init_random() {
	srand(time(NULL));
	for (int i = 0; i < 60; i++) { srand(randint(0, 100000000)); }
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

int main() {
	cout << write("test.txt", "Test") << endl;
	cout << read("test.txt") << endl;
	cout << exists("test.txt") << endl << endl;;

	init_random();
	for (int i = 0; i < 15; i++) cout << randint(0, 100) << endl;

	cout << endl;

	string random_key = "";
	string ascii_list = get_ascii_list();

	for (int i = 0; i < randint(10, 100); i++) {
		random_key += ascii_list[randint(0, ascii_list.length()-1)];
	}
	cout << random_key << endl;

	// cout << get_ascii_uppercase() << endl;
	// cout << get_ascii_list() << endl;

	string uppercase = get_ascii_uppercase();
	auto random_uppercase_letter = uppercase[randint(0, uppercase.length()-1)];
	string random_int_string = to_string(randint(100, 999));
	cout << random_uppercase_letter + random_int_string << endl;
}