#include <iostream>

int main() {
    // Вывод ASCII символов от 65 до 90 (A-Z)
    for (int i = 65; i <= 90; i++) {
        char asciiChar = static_cast<char>(i);
        std::cout << asciiChar << " ";
    }
    
    std::cout << std::endl;
    
    // Вывод ASCII символов от 97 до 122 (a-z)
    for (int j = 97; j <= 122; j++) {
        char asciiChar = static_cast<char>(j);
        std::cout << asciiChar << " ";
    }
    
    return 0;
}