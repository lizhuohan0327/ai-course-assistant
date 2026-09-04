#include <iostream>
#include <stack>
#include <string>
using namespace std;

bool match(char left, char right) {
    return (left == '(' && right == ')') ||
           (left == '[' && right == ']') ||
           (left == '{' && right == '}');
}

bool validBrackets(const string& s) {
    stack<char> st;

    for (char c : s) {
        if (c == '(' || c == '[' || c == '{') {
            st.push(c);
        } else if (c == ')' || c == ']' || c == '}') {
            if (st.empty()) return false;
            if (!match(st.top(), c)) return false;
            st.pop();
        }
    }
    return st.empty();
}

int main() {
    string s;
    getline(cin, s);
    cout << (validBrackets(s) ? "Valid" : "Invalid") << "\n";
    return 0;
}
