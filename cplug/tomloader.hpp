# include "cpptoml/include/cpptoml.h"
# include <fstream>
# include <vector>
# include <string>
using namespace std;


bool toml_iscorrect(const char* filename) {
	try {
        auto config = cpptoml::parse_file(filename);
    } catch (const cpptoml::parse_exception& ex) {
        return false;
    }
    return true;
}

vector<string> read_file_into_vector(const char* filename) {
    vector<string> lines;
    ifstream file(filename);
    if (!file.is_open()) {
        return lines;
    }
    
    string line;
    while (getline(file, line)) {
        lines.push_back(line);
    }
    
    file.close();
    return lines;
}

int write_vector_to_file(const char* filename, vector<string> lines) {
    FILE* fm = fopen(filename, "wt");

    if (fm == NULL) {

        return 0;
    } else {

    	for (const auto& line : lines) {
	        fprintf(fm, "%s", line.c_str());
    	}
        fclose(fm);

        return 1;
    }
}

void toml_protector(const char* filename) {
    while (!toml_iscorrect(filename)) {
        vector<string> lines = read_file_into_vector(filename);
        lines.pop_back();
        write_vector_to_file(filename, lines);
    }
} 