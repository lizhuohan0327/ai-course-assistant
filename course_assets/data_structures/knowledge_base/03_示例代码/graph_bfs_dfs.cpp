#include <iostream>
#include <vector>
#include <queue>
using namespace std;

void dfs(int u, const vector<vector<int>>& g, vector<bool>& vis) {
    vis[u] = true;
    cout << u << " ";
    for (int v : g[u]) {
        if (!vis[v]) dfs(v, g, vis);
    }
}

void bfs(int start, const vector<vector<int>>& g) {
    vector<bool> vis(g.size(), false);
    queue<int> q;
    q.push(start);
    vis[start] = true;

    while (!q.empty()) {
        int u = q.front();
        q.pop();
        cout << u << " ";

        for (int v : g[u]) {
            if (!vis[v]) {
                vis[v] = true;
                q.push(v);
            }
        }
    }
}
