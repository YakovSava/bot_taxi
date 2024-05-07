# include <fstream>
# include <string>
using namespace std;

void write(string filename, string all_lines) {
	ofstream file;
	file.open(filename.c_str());
	if (file.is_open()) {
		file << all_lines << endl;
		file.close();
	}
}