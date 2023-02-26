# include <fstream>
# include <string>
using namespace std;

int write(string filename, string all_lines) {
	ofstream file;
	file.open(filename.c_str());
	if (file.is_open()) {
		file << all_lines << endl;
		file.close();
		return 1;
	} else {
		return 0;
	}
}