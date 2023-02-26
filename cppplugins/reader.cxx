# include <fstream>
# include <string>
using namespace std;

string read(string filename) {
	ifstream file;
	string line, lines = "", endline = "\n";
	file.open(filename.c_str());
	if (file.is_open()) {
		while (getline(file, line)) {
			lines = lines + endline + line;
		}
	} else {
		lines = "Bad open";
	}
	file.close();
	return lines;
}