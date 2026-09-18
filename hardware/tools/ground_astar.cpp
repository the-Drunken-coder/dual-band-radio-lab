// Clearance-grid A*. Input masks are geometry inflated by trace/via clearance.
// Native KiCad DRC remains authoritative; this tool does not waive violations.
#include <vector>
#include <queue>
#include <fstream>
#include <cmath>
#include <iostream>
#include <cstdint>
using namespace std;
struct Node {float f,g;int id;bool operator<(const Node&o)const{return f>o.f;}};
int main(int argc,char**argv){
 ifstream in(argv[1],ios::binary);int w,h,ns,ng,allow;in.read((char*)&w,4);in.read((char*)&h,4);in.read((char*)&ns,4);in.read((char*)&ng,4);in.read((char*)&allow,4);
 float back=argc>3?stof(argv[3]):35.f;int N=w*h;vector<uint8_t> occ(N*2),via(N),goal(N*2);in.read((char*)occ.data(),N*2);in.read((char*)via.data(),N);
 vector<int> starts(ns),goals(ng);in.read((char*)starts.data(),ns*4);in.read((char*)goals.data(),ng*4);
 int xmin=w,xmax=0,ymin=h,ymax=0;for(int a:goals){goal[a]=1;int x=a%N%w,y=a%N/w;xmin=min(xmin,x);xmax=max(xmax,x);ymin=min(ymin,y);ymax=max(ymax,y);}
 auto heur=[&](int i){int x=i%N%w,y=i%N/w;return hypot(float(max({xmin-x,0,x-xmax})),float(max({ymin-y,0,y-ymax})));};
 vector<float> cost(N*2,1e30);vector<int> prev(N*2,-1);priority_queue<Node> q;
 for(int a:starts)if(!occ[a]){cost[a]=0;q.push({heur(a),0,a});}
 int end=-1;long visits=0;
 while(!q.empty()){
 auto a=q.top();q.pop();if(a.g!=cost[a.id])continue;if(goal[a.id]){end=a.id;break;}visits++;
 int l=a.id/N,y=a.id%N/w,x=a.id%w;
 auto add=[&](int id,float d){float c=a.g+d;if(c<cost[id]){cost[id]=c;prev[id]=a.id;q.push({c+heur(id),c,id});}};
 for(int dy=-1;dy<=1;dy++)for(int dx=-1;dx<=1;dx++)if(dx||dy){int xx=x+dx,yy=y+dy;if(xx<0||xx>=w||yy<0||yy>=h)continue;int id=l*N+yy*w+xx;if(occ[id])continue;if(dx&&dy&&(occ[l*N+y*w+xx]||occ[l*N+yy*w+x]))continue;add(id,(dx&&dy?1.414214f:1.f)*(l?back:1.f));}
 if(allow&&!via[y*w+x]&&!occ[(1-l)*N+y*w+x])add((1-l)*N+y*w+x,40);
 }
 ofstream out(argv[2],ios::binary);vector<int> path;
 if(end>=0){for(int a=end;a>=0;a=prev[a])path.push_back(a);reverse(path.begin(),path.end());}int size=path.size();out.write((char*)&size,4);out.write((char*)path.data(),size*4);cerr<<" nodes="<<visits<<" path="<<size<<"\n";
}
