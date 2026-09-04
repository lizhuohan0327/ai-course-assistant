#include <iostream>
using namespace std;

struct Node {
    int data;
    Node* next;
    Node(int x) : data(x), next(nullptr) {}
};

void pushFront(Node*& head, int x) {
    Node* node = new Node(x);
    node->next = head;
    head = node;
}

bool removeValue(Node*& head, int x) {
    Node* cur = head;
    Node* prev = nullptr;

    while (cur) {
        if (cur->data == x) {
            if (prev) prev->next = cur->next;
            else head = cur->next;
            delete cur;
            return true;
        }
        prev = cur;
        cur = cur->next;
    }
    return false;
}

void printList(Node* head) {
    while (head) {
        cout << head->data << " ";
        head = head->next;
    }
    cout << "\n";
}

void destroy(Node*& head) {
    while (head) {
        Node* tmp = head;
        head = head->next;
        delete tmp;
    }
}

int main() {
    Node* head = nullptr;
    pushFront(head, 3);
    pushFront(head, 2);
    pushFront(head, 1);

    printList(head);
    removeValue(head, 2);
    printList(head);

    destroy(head);
    return 0;
}
