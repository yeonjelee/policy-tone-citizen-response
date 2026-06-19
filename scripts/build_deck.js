const pptxgen=require("pptxgenjs");
const p=new pptxgen();
p.defineLayout({name:"W",width:13.33,height:7.5}); p.layout="W"; p.title="정책 어조에 따른 시민 반응 분석";
const PR="/sessions/laughing-zen-allen/mnt/정책 어조에 따른 시민 반응 분석 프로젝트";
const F="Calibri";
const BAND="1F4E79",ACCBAR="5B9BD5",SUBTXT="CFE0F0",WHITE="FFFFFF";
const HEAD="1A2230",INK="2A3340",BODY="333B47",MUT="6B7480",FAINT="9AA3AE",HAIR="E1E5EB",BOX="F2F4F7",ACC="1F4E79";
const GREEN="2F7D4F",RED="C0392B",AMBER="B7791F",TEAL="2C7A7B",PURP="5A4FCF";
const W=13.33,H=7.5,TOT=14;
function bl(c1,c2,t){const a=parseInt(c1,16),b=parseInt(c2,16);const r=Math.round(((a>>16)&255)*(1-t)+((b>>16)&255)*t),g=Math.round(((a>>8)&255)*(1-t)+((b>>8)&255)*t),x=Math.round((a&255)*(1-t)+(b&255)*t);return((1<<24)+(r<<16)+(g<<8)+x).toString(16).slice(1).toUpperCase();}
function head(s,title,n,sub){s.background={color:WHITE};
 s.addShape(p.shapes.RECTANGLE,{x:0,y:0,w:W,h:0.92,fill:{color:BAND},line:{type:"none"}});
 s.addShape(p.shapes.RECTANGLE,{x:0,y:0,w:0.14,h:0.92,fill:{color:ACCBAR},line:{type:"none"}});
 s.addText(title,{x:0.5,y:0,w:8.7,h:0.92,fontFace:F,fontSize:21,bold:true,color:WHITE,valign:"middle",margin:0});
 s.addText([{text:"정책 어조에 따른 시민 반응 분석",options:{breakLine:true,fontSize:10.5,color:SUBTXT}},{text:`${n} / ${TOT}`,options:{fontSize:12,bold:true,color:WHITE}}],{x:W-3.5,y:0,w:3.1,h:0.92,align:"right",valign:"middle",margin:0});
 if(sub)s.addText(sub,{x:0.5,y:1.02,w:W-1.0,h:0.4,fontFace:F,fontSize:13.5,bold:true,color:ACC,margin:0});}
function box(s,x,y,w,h){s.addShape(p.shapes.ROUNDED_RECTANGLE,{x,y,w,h,fill:{color:BOX},line:{color:HAIR,width:1},rectRadius:0.08});}
function th(t){return{text:t,options:{fill:{color:BAND},color:WHITE,bold:true,fontFace:F,fontSize:11.5}};}
const MX=0.5;

// 1 표지
let s=p.addSlide(); s.background={color:WHITE};
s.addShape(p.shapes.RECTANGLE,{x:0,y:0,w:W,h:0.55,fill:{color:BAND},line:{type:"none"}});
s.addShape(p.shapes.RECTANGLE,{x:0,y:H-0.35,w:W,h:0.35,fill:{color:BAND},line:{type:"none"}});
s.addText("데이터분석 및 활용 · 개인 프로젝트 결과 보고서",{x:0.9,y:1.9,w:11.5,h:0.4,fontFace:F,fontSize:14,color:MUT,margin:0});
s.addText("정책 어조에 따른 시민 반응 분석",{x:0.9,y:2.5,w:11.5,h:1.0,fontFace:F,fontSize:40,bold:true,color:HEAD,margin:0});
s.addText("통화·재정정책 어조와 시민 검색·실현행동 반응의 국면 분석 (2016–2024)",{x:0.9,y:3.6,w:11.5,h:0.5,fontFace:F,fontSize:16,color:BODY,margin:0});
box(s,0.9,4.5,11.53,1.5);
s.addText([{text:"분석 기법    ",options:{bold:true,color:ACC}},{text:"어조 분류 · 잠재국면 군집 · 구조적 단절 탐지 · 편상관 · 사건연구(event study) · 플랫폼 외적타당성 검증",options:{color:BODY,breakLine:true}},{text:"분석 단위    ",options:{bold:true,color:ACC}},{text:"월별 패널 + 일별 사건연구 데이터 (2016-01 ~ 2024-12)",options:{color:BODY}}],{x:1.2,y:4.7,w:11.0,h:1.1,fontFace:F,fontSize:13,valign:"middle",lineSpacingMultiple:1.4});

// 2 개요
s=p.addSlide(); head(s,"프로젝트 개요",2);
box(s,MX,1.15,W-2*MX,1.35);
s.addText("거시경제 이론(비교정태)은 정책이 작동하는 ‘방향’을 제시하지만, 시민이 그 정책에 어떤 ‘속도·경로’로 반응하는지, 또 그 반응을 사전에 예측해 활용할 수 있는지는 답하지 못한다. 본 연구는 한국은행·기획재정부의 정책 어조를 텍스트마이닝으로 수치화하고, 이를 시민의 검색(주의)·실현행동·언론보도·금융시장 데이터와 결합해 정책–시민 반응 구조를 실증한다.",{x:MX+0.3,y:1.25,w:W-2*MX-0.6,h:1.15,fontFace:F,fontSize:13,color:BODY,valign:"middle",lineSpacingMultiple:1.2});
box(s,MX,2.65,W-2*MX,0.95);
s.addText([{text:"연구가설    ",options:{bold:true,color:ACC,fontSize:13.5}},{text:"H1. 정책기조(긴축/완화)의 변화가 시민 반응(검색)과 이론 정합적 공행성을 보이는가?   ·   H2. 동일 정책에서도 언론 보도논조에 따라 반응이 조절(moderation)되는가? (보조)",options:{color:INK,fontSize:12.5}}],{x:MX+0.3,y:2.65,w:W-2*MX-0.6,h:0.95,fontFace:F,valign:"middle"});
box(s,MX,3.75,6.05,2.55); box(s,MX+6.28,3.75,6.0,2.55);
s.addText([{text:"분석 자료",options:{bold:true,color:HEAD,fontSize:13.5,breakLine:true}},{text:"정책 어조: 통화정책 결정문 77·금통위 의사록 77·기재부 재정문서",options:{bullet:true,breakLine:true}},{text:"시민 반응: 네이버·구글·유튜브 검색지수, 빅카인즈 기사 27,497건",options:{bullet:true,breakLine:true}},{text:"실측·통제: ECOS/KOSIS 거시변수, 금융시장(원/달러·KOSPI), 실현행동(가계대출·예금·주택가격·예탁금), 인구통계",options:{bullet:true}}],{x:MX+0.3,y:3.95,w:5.5,h:2.2,fontFace:F,fontSize:12,color:BODY,lineSpacingMultiple:1.12});
s.addText([{text:"분석 절차",options:{bold:true,color:HEAD,fontSize:13.5,breakLine:true}},{text:"① 정책문서 어조 라벨링 (분류)",options:{bullet:true,breakLine:true}},{text:"② 잠재국면 군집화 (메인 분석)",options:{bullet:true,breakLine:true}},{text:"③ 구조적 단절(이례 시점) 탐지",options:{bullet:true,breakLine:true}},{text:"④ 편상관·시차·사건연구로 반응구조 규명",options:{bullet:true,breakLine:true}},{text:"⑤ 플랫폼 교차검증·인구통계 세분화",options:{bullet:true}}],{x:MX+6.58,y:3.95,w:5.45,h:2.2,fontFace:F,fontSize:12,color:BODY,lineSpacingMultiple:1.12});

// 3 AI
s=p.addSlide(); head(s,"AI 도구 활용 내역 보고",3);
box(s,MX,1.15,W-2*MX,0.95);
s.addText("LLM(Claude)은 ‘보조 도구’로 활용하였다. 데이터 수집·정제 코드 구현, 디버깅, 시각화 등 반복·기술 작업의 효율화에 사용하였으며, 연구설계·방법론·해석 등 학술적 판단은 연구자 본인이 수행하였다. 역할 구분은 다음과 같다.",{x:MX+0.3,y:1.15,w:W-2*MX-0.6,h:0.95,fontFace:F,fontSize:13,color:BODY,valign:"middle",lineSpacingMultiple:1.18});
s.addTable([[{text:"Claude(LLM) — 구현·보조",options:{fill:{color:BAND},color:WHITE,bold:true,fontFace:F,fontSize:13}},{text:"연구자 본인 — 판단·결정",options:{fill:{color:BAND},color:WHITE,bold:true,fontFace:F,fontSize:13}}],
 ["데이터 수집·크롤링 코드 구현 및 오류 디버깅","연구가설(H1/H2)·분석 동기 설정"],["eKoNLPy 감성사전 시드 적용, 재정 어조사전 초안","어조 부호 체계 정의(긴축=+1 통일)"],["통계·군집·시각화 코드 작성","중첩 군집·사건연구·정보위계 설계"],["PDF 본문 재수집·전처리, 플랫폼·시장 수집","편상관·시차·일별화·교차검증 방향 지시"],["결과 표·도표 산출","결과 해석·한계 판단 및 분석 전반의 의사결정"]],
 {x:MX,y:2.3,w:W-2*MX,colW:[(W-2*MX)/2,(W-2*MX)/2],rowH:0.58,fontFace:F,fontSize:12.5,color:BODY,valign:"middle",border:{type:"solid",pt:1,color:HAIR}});
s.addText("원칙: 반복·구현은 도구로 효율화하되, 방법론적 의사결정과 학술적 판단의 주체는 연구자임을 명시한다.",{x:MX,y:6.55,w:W-2*MX,h:0.4,fontFace:F,fontSize:10.5,italic:true,color:FAINT,margin:0});

// 4 기초분석
s=p.addSlide(); head(s,"데이터 기초 분석 결과",4,"어조 지수 타당성 — 정책 사이클 재현 검증");
box(s,MX,1.55,W-2*MX,0.7);
s.addText("본격 분석에 앞서 텍스트에서 산출한 어조 지수(tone index)가 실제 정책 흐름을 반영하는지 검증하였다. 4개 어조 축을 −1(완화)~+1(긴축)으로 산출해 연도별로 비교한 결과, 실제 금리·재정 정책 사이클과 정합적이었다.",{x:MX+0.3,y:1.55,w:W-2*MX-0.6,h:0.7,fontFace:F,fontSize:12.5,color:BODY,valign:"middle",lineSpacingMultiple:1.15});
const yl=["2016","2017","2018","2019","2020","2021","2022","2023","2024"];
s.addChart(p.charts.LINE,[{name:"물가(긴축)",labels:yl,values:[-0.17,0.15,0.23,-0.20,-0.26,0.26,0.38,0.15,0.02]},{name:"성장(긴축)",labels:yl,values:[-0.36,0.07,0.10,-0.31,-0.40,0.05,0.08,-0.09,-0.09]},{name:"금융안정",labels:yl,values:[-0.40,-0.23,-0.26,-0.36,-0.50,-0.21,-0.12,-0.18,-0.33]},{name:"재정(긴축)",labels:yl,values:[0.23,-0.48,-0.77,-0.72,-0.72,-0.73,-0.18,0.08,-0.09]}],{x:MX,y:2.45,w:7.6,h:3.95,chartColors:[ACC,TEAL,AMBER,RED],lineSize:2.25,lineSmooth:true,showLegend:true,legendPos:"b",legendFontFace:F,legendFontSize:11,catAxisLabelFontFace:F,valAxisLabelFontFace:F,catAxisLabelColor:MUT,valAxisLabelColor:MUT,valGridLine:{color:HAIR,size:0.5},catGridLine:{style:"none"},valAxisMinVal:-1,valAxisMaxVal:0.6});
box(s,8.4,2.45,W-MX-8.4,3.95);
s.addText([{text:"해석",options:{bold:true,color:ACC,fontSize:13.5,breakLine:true}},{text:"물가 어조: 2018·2022 금리 인상기에 긴축 정점, 2020 코로나 완화기에 음(−)으로 반전.",options:{bullet:true,breakLine:true}},{text:"재정 어조: 2017–2021 확장 → 2023 건전화로 기조 전환.",options:{bullet:true,breakLine:true}},{text:"→ 텍스트 기반 어조가 실제 정책 사이클을 재현, 측정 타당성(measurement validity) 확보.",options:{color:ACC,bold:true}}],{x:8.65,y:2.65,w:3.65,h:3.6,fontFace:F,fontSize:12,color:BODY,lineSpacingMultiple:1.15});
s.addText("방법론·참고문헌: 중앙은행 어조 지수 측정(Apel & Blix Grimaldi, Riksbank) · 매파–비둘기 척도(Hawkish-Dovish Index, Picault·Renault).",{x:MX,y:6.55,w:W-2*MX,h:0.35,fontFace:F,fontSize:9.5,italic:true,color:FAINT,margin:0});

// 5 전처리
s=p.addSlide(); head(s,"데이터 전처리 결과",5,"어조 지수 산출 파이프라인");
box(s,MX,1.55,W-2*MX,0.6);
s.addText("어조 지수는 [문장 분할 → 정책 축 태깅 → 방향 점수화 → 월별 집계] 4단계로 산출하였다. 수집·정제 과정의 주요 난점도 함께 해결하였다.",{x:MX+0.3,y:1.55,w:W-2*MX-0.6,h:0.6,fontFace:F,fontSize:12.5,color:BODY,valign:"middle"});
[["①","문장 분할","형태소분석기 kiwipiepy"],["②","정책 축 태깅","물가·성장·금융안정·재정 4축 배정"],["③","방향 점수화","감성사전 기반 (P−N)/(P+N)"],["④","월별 집계","기조 지속 가정 LOCF"]].forEach((st,i)=>{const x=MX+i*3.07;box(s,x,2.35,2.85,1.5);s.addText(st[0],{x:x+0.2,y:2.45,w:0.6,h:0.45,fontFace:F,fontSize:20,bold:true,color:ACC,margin:0});s.addText([{text:st[1],options:{bold:true,breakLine:true,fontSize:13,color:HEAD}},{text:st[2],options:{fontSize:10.5,color:MUT}}],{x:x+0.2,y:2.9,w:2.5,h:0.9,fontFace:F,margin:0,lineSpacingMultiple:1.05});});
box(s,MX,4.1,W-2*MX,2.25);
s.addText([{text:"수집·정제 과정에서 해결한 주요 문제",options:{bold:true,color:HEAD,fontSize:13.5,breakLine:true}},{text:"어조 부호 통일: 긴축(+1)/완화·확장(−1) — Hawkish-Dovish 지수·eKoNLPy 표준 준용.",options:{bullet:true,breakLine:true}},{text:"본문 재수집: 한은·기재부 보도자료 본문이 첨부 PDF에 존재 → 목록이 아닌 PDF에서 본문 추출.",options:{bullet:true,breakLine:true}},{text:"재정 어조: eKoNLPy(통화 전용)에 재정 어휘 부재 → 건전화/확장 자작 어조사전 별도 구축.",options:{bullet:true,breakLine:true}},{text:"검색(월·일·플랫폼3)·거시·시장·기사 자료를 단일 월별 패널로 결합.",options:{bullet:true}}],{x:MX+0.3,y:4.3,w:W-2*MX-0.6,h:1.95,fontFace:F,fontSize:12.5,color:BODY,lineSpacingMultiple:1.18});
s.addText("방법론·참고문헌: 통화 어조 시드사전 eKoNLPy(박기영 외, 「의사록 텍스트마이닝」, 한국은행) · 방향 점수 net-tone=(P−N)/(P+N), 어조 부호 −1~+1.",{x:MX,y:6.45,w:W-2*MX,h:0.35,fontFace:F,fontSize:9.5,italic:true,color:FAINT,margin:0});

// 6 마이닝 ① H1
s=p.addSlide(); head(s,"데이터 마이닝 결과 ①",6,"동조성(공행성) 분석 (H1) — 정책 긴축과 검색 반응의 이론 정합");
box(s,MX,1.55,W-2*MX,0.72);
s.addText("정책 긴축(+1) 시 각 검색지수가 이론상 가져야 할 부호(기대부호)를 설정하고, 실제 시차 교차상관과 비교하였다(초록=정합, 빨강=괴리). 거시변수 통제 후에도 관계가 유지되는지 편상관(partial correlation)으로 확인하였다.",{x:MX+0.3,y:1.55,w:W-2*MX-0.6,h:0.72,fontFace:F,fontSize:12.5,color:BODY,valign:"middle",lineSpacingMultiple:1.15});
const cols=["","예금","대출","부동산","물가","환율","투자"];
const Mt=[["물가(긴축)",0.39,-0.16,-0.16,0.44,0.13,0.46],["성장(긴축)",0.27,0.01,0.02,0.32,0.04,0.41],["금융안정",0.45,-0.17,-0.11,null,0.28,0.50],["재정(긴축)",0.35,0.00,-0.10,0.07,null,0.40]];
function hc(v){if(v===null)return{f:"EAECEF",c:"6B7480"};if(v>0){const a=Math.min(1,Math.abs(v)/0.5);return{f:bl("FFFFFF",GREEN,a*0.66),c:"17402A"};}const a=Math.min(1,Math.abs(v)/0.18);return{f:bl("FFFFFF",RED,a*0.66),c:"5C1A14"};}
const hr=[cols.map(c=>({text:c,options:{fill:{color:BAND},color:WHITE,bold:true,fontFace:F,fontSize:12,align:"center"}}))];
Mt.forEach(row=>{const r=[{text:row[0],options:{fill:{color:BOX},color:HEAD,bold:true,fontFace:F,fontSize:12}}];for(let j=1;j<7;j++){const v=row[j],c=hc(v);r.push({text:v===null?"무관":v.toFixed(2),options:{fill:{color:c.f},color:c.c,bold:true,fontFace:F,fontSize:12,align:"center"}});}hr.push(r);});
s.addTable(hr,{x:MX,y:2.45,w:8.0,colW:[1.6,1.06,1.06,1.06,1.06,1.06,1.06],rowH:0.46,valign:"middle",border:{type:"solid",pt:1.5,color:WHITE}});
box(s,8.7,2.45,W-MX-8.7,2.2);
s.addText("거시 통제 효과 (이론 정합률)",{x:8.95,y:2.62,w:3.4,h:0.35,fontFace:F,fontSize:11.5,bold:true,color:MUT,margin:0});
s.addText([{text:"73%",options:{fontSize:23,bold:true,color:FAINT}},{text:"  →  ",options:{fontSize:14,color:FAINT}},{text:"82%",options:{fontSize:34,bold:true,color:ACC}}],{x:8.95,y:3.0,w:3.4,h:0.75,fontFace:F,margin:0});
s.addText("금리·CPI·환율·KOSPI·실업률 통제 편상관 기준",{x:8.95,y:3.85,w:3.4,h:0.6,fontFace:F,fontSize:10.5,color:MUT,margin:0,lineSpacingMultiple:1.1});
box(s,MX,4.9,W-2*MX,1.5);
s.addText([{text:"검색은 대체로 정책기조와 이론 정합적으로 공행한다(통제 후 82%). 다만 긴축기 ",options:{color:BODY}},{text:"대출·부동산 검색만 이론과 역행(↑)",options:{color:RED,bold:true}},{text:"하는 ‘겉보기 역설’이 관측된다. 이론 정합률(82%)은 결과의 결론이 아니라, 괴리 지점과 반응 동학을 해석하기 위한 ",options:{color:BODY}},{text:"기준선(baseline)",options:{color:ACC,bold:true}},{text:"이다 (→ 결과 설명).",options:{color:BODY}}],{x:MX+0.3,y:5.05,w:W-2*MX-0.6,h:1.1,fontFace:F,fontSize:12.5,valign:"middle",lineSpacingMultiple:1.18});
s.addText("방법: 시차 순위상관(Spearman, lag 0–3 중 이론정합 최대) · 거시 통제는 순위 잔차화 편상관(금리·CPI·환율·KOSPI·실업률).",{x:MX,y:6.5,w:W-2*MX,h:0.35,fontFace:F,fontSize:9.5,italic:true,color:FAINT,margin:0});

// 7 마이닝 ② 군집
s=p.addSlide(); head(s,"데이터 마이닝 결과 ②",7,"잠재국면 군집 — 2단계 중첩 군집(계층군집 + K-평균) · t-SNE 사상");
box(s,MX,1.55,W-2*MX,0.72);
s.addText("정책기조(어조 4축)로 1차 계층군집(Ward 연결), 각 기조 내 시민반응(검색 6축)으로 2차 K-평균을 적용하는 중첩 군집으로 잠재국면을 도출하였다. 군집수는 실루엣 계수로 선택(1단계 K=2, 실루엣 0.40), 고차원 군집은 t-SNE(perplexity≈min(30,n/4))로 2차원 사상하여 분리도를 확인하였다.",{x:MX+0.3,y:1.55,w:W-2*MX-0.6,h:0.72,fontFace:F,fontSize:12.5,color:BODY,valign:"middle",lineSpacingMultiple:1.15});
s.addImage({path:PR+"/processed/figures/tsne.png",x:MX,y:2.5,w:4.5,h:3.7});
s.addText("t-SNE 2차원 사상 (축은 비해석적, 군집 분리도만 표시)",{x:MX,y:6.2,w:4.6,h:0.3,fontFace:F,fontSize:9.5,italic:true,color:FAINT,margin:0});
s.addTable([[th("국면"),th("기간"),th("기준금리"),th("n"),th("국면 특징")],
 [{text:"0-1",options:{bold:true,color:RED}},"’22–’24","3.42%","23","고금리 고착 · 부동산·대출 반발"],
 [{text:"0-0",options:{bold:true,color:AMBER}},"’21–’22","1.14%","19","긴축 전환 · 부동산 광풍"],
 [{text:"0-2",options:{bold:true,color:ACC}},"’17–’19","1.45%","25","완만 긴축 · 확장재정"],
 [{text:"1-1",options:{bold:true,color:TEAL}},"’16–’20","1.28%","24","저금리 · 부동산 과열"],
 [{text:"1-2",options:{bold:true,color:PURP}},"’20–’21","0.50%","8","코로나 완화 · 레버리지 확대"],
 [{text:"1-0",options:{bold:true,color:FAINT}},"산발","2.61%","7","대외충격(외환) 전이"]],
 {x:5.35,y:2.45,w:7.45,h:3.75,colW:[0.9,1.25,1.2,0.6,3.5],rowH:0.6,fontFace:F,fontSize:11.5,color:BODY,valign:"middle",border:{type:"solid",pt:0.5,color:HAIR}});
s.addText("방법: 1단계 Ward 계층군집 K=2(실루엣 0.40), 2단계 K-평균(실루엣 0.39–0.45), t-SNE perplexity≈min(30,n/4). 거시·괴리는 군집 피처가 아닌 사후 프로파일링에만 사용(순환논리 방지) — 국면은 자료에서 발견된 유형.",{x:MX,y:6.5,w:W-2*MX,h:0.45,fontFace:F,fontSize:9.5,italic:true,color:FAINT,margin:0});

// 8 마이닝 ③ 이상치
s=p.addSlide(); head(s,"데이터 마이닝 결과 ③",8,"구조적 단절(structural break) 탐지 — 이론 괴리 z-점수 + 국소 이상치 계수(LOF)");
box(s,MX,1.55,W-2*MX,1.0);
s.addText([{text:"정책–시민 공행 관계가 기존 구조에서 이탈한 시점을 두 지표로 탐지하였다.  ",options:{color:BODY}},{text:"① 이론 괴리 지수 z(D): ",options:{bold:true,color:ACC}},{text:"기대부호와 표준화 변수의 곱으로 정의한 이론 위반량을 표준화, |z|>2σ를 이례치로 식별.  ",options:{color:BODY}},{text:"② 국소 이상치 계수(LOF): ",options:{bold:true,color:ACC}},{text:"어조 4축+검색 6축 다변량 공간의 국소 밀도 기반 이상도. 탐지된 이례 시점을 외생충격과 대응시켰다.",options:{color:BODY}}],{x:MX+0.3,y:1.55,w:W-2*MX-0.6,h:1.0,fontFace:F,fontSize:12.5,valign:"middle",lineSpacingMultiple:1.2});
s.addTable([[th("시점"),th("z(D)"),th("LOF"),th("외생충격 / 주도 채널"),th("판정")],
 ["2020-03","3.80","●","코로나 팬데믹 — 외환 급등·긴급 완화 동시충격","구조적 단절"],
 ["2024-12","3.73","●","정치적 불확실성(비상계엄) — 원/달러 급등","구조적 단절"],
 ["2019-05","2.35","–","미·중 무역분쟁 · 디스인플레이션","구조적 단절"],
 ["2022-10","1.67","●","신용경색(레고랜드) · 부동산 경착륙","구조적 단절"],
 ["2016 초","2.4","●","재정 어조 표본 희소(MOEF 문서 부족)","측정오차(아티팩트)"]],
 {x:MX,y:2.75,w:W-2*MX,colW:[1.5,1.0,0.9,6.0,2.93],rowH:0.6,fontFace:F,fontSize:12,color:BODY,valign:"middle",align:"center",border:{type:"solid",pt:0.5,color:HAIR}});
s.addText("방법: z(D)=Σ max(−E·z(어조)·z(검색),0), 임계 |z|>2σ · LOF n_neighbors=min(20,max(5,n/6)), 피처 z(어조4+검색6) [Breunig 외, LOF]. ‘구조적 단절 vs 측정오차’ 구분으로 해석 정직성 확보.",{x:MX,y:6.5,w:W-2*MX,h:0.45,fontFace:F,fontSize:9.5,italic:true,color:FAINT,margin:0});

// 9 마이닝 ④ 사건연구
s=p.addSlide(); head(s,"데이터 마이닝 결과 ④",9,"사건연구(event study) — 정책 결정 직후 주의(검색)의 즉각 반응");
box(s,MX,1.55,W-2*MX,0.72);
s.addText("금통위 결정일 77건을 사건일(t=0)로 정렬하고, 결정 전후 일별 검색을 직전 10일 평균=100으로 지수화해 평균하였다(요일효과는 7일 중심이동평균으로 제거). 정책 직후 시민 ‘주의(attention)’의 반응 속도를 일별 해상도로 식별한다.",{x:MX+0.3,y:1.55,w:W-2*MX-0.6,h:0.72,fontFace:F,fontSize:12.5,color:BODY,valign:"middle",lineSpacingMultiple:1.15});
const ev=["-10","-7","-3","0","+3","+7","+14","+21","+28"];
s.addChart(p.charts.LINE,[{name:"예금",labels:ev,values:[108,95,101,108,117,113,107,101,102]},{name:"대출",labels:ev,values:[105,96,100,102,103,98,96,97,98]},{name:"물가",labels:ev,values:[105,98,99,103,107,104,99,104,112]},{name:"환율",labels:ev,values:[111,94,97,98,99,98,97,100,108]}],{x:MX,y:2.5,w:7.5,h:3.85,chartColors:[ACC,TEAL,RED,AMBER],lineSize:2.25,lineSmooth:true,showLegend:true,legendPos:"b",legendFontFace:F,legendFontSize:11,catAxisTitle:"사건일(정책 결정일=0) 기준 일수",showCatAxisTitle:true,catAxisTitleFontFace:F,catAxisTitleFontSize:10.5,catAxisLabelFontFace:F,valAxisLabelFontFace:F,catAxisLabelColor:MUT,valAxisLabelColor:MUT,valGridLine:{color:HAIR,size:0.5},catGridLine:{style:"none"},valAxisMinVal:90,valAxisMaxVal:120});
box(s,8.4,2.5,W-MX-8.4,3.85);
s.addText([{text:"해석",options:{bold:true,color:ACC,fontSize:13.5,breakLine:true}},{text:"예금 검색은 사건 직후 1주 +17%(매파 결정 시 +25%) 급등 후 2주 내 정상화 — 주의는 즉각·일시적.",options:{bullet:true,breakLine:true}},{text:"물가·대출 검색은 일별 기사량이 약 4일 선행(시차 교차상관 ρ=0.24/0.15) — 시민은 정책에 직접보다 보도를 매개로 반응.",options:{bullet:true,breakLine:true}},{text:"→ 비교정태가 다루지 않는 ‘반응의 속도·전달경로’를 일별 자료로 규명.",options:{color:ACC,bold:true}}],{x:8.65,y:2.7,w:3.65,h:3.5,fontFace:F,fontSize:11.5,color:BODY,lineSpacingMultiple:1.15});
s.addText("방법: 추정창 [−10,+30]일, 기준창=직전 10일 평균, 요일효과 7일 중심이동평균 제거 · 시장 사건연구 [−5,+5] · 정책→보도 전이는 시차 교차상관 [MacKinlay, Event Studies in Economics and Finance].",{x:MX,y:6.5,w:W-2*MX,h:0.45,fontFace:F,fontSize:9.5,italic:true,color:FAINT,margin:0});

// 10 마이닝 ⑤ 플랫폼
s=p.addSlide(); head(s,"데이터 마이닝 결과 ⑤",10,"외적 타당성 — 검색 플랫폼 교차검증(네이버·구글·유튜브)");
box(s,MX,1.55,W-2*MX,0.6);
s.addText("단일 플랫폼(네이버) 결과의 우연성을 배제하기 위해, 동일 검색어를 구글·유튜브(Google Trends YouTube 검색 속성)로도 수집해 비교하였다. 검색어는 모두 한국어·한국(geo=KR) 기준이다.",{x:MX+0.3,y:1.55,w:W-2*MX-0.6,h:0.6,fontFace:F,fontSize:12.5,color:BODY,valign:"middle"});
s.addTable([[th("검색축"),th("네이버~구글"),th("네이버~유튜브"),th("긴축→네이버"),th("긴축→구글")],["예금","0.91","0.84","+0.16","+0.32"],["대출","0.82","0.60","+0.10","+0.13"],["물가","0.65","0.62","+0.40","+0.39"],["부동산","0.39","0.67","+0.16","+0.18"],["환율","0.85","0.76","−0.06","−0.02"],["투자","0.19","−0.22","−0.29","−0.10"]],{x:MX,y:2.35,w:7.5,h:3.6,colW:[1.5,1.5,1.5,1.5,1.5],rowH:0.5,fontFace:F,fontSize:12,color:BODY,valign:"middle",align:"center",border:{type:"solid",pt:0.5,color:HAIR}});
box(s,8.4,2.35,W-MX-8.4,3.6);
s.addText([{text:"해석",options:{bold:true,color:ACC,fontSize:13.5,breakLine:true}},{text:"예금·환율·대출은 네이버~구글 순위상관 0.82~0.91 — 플랫폼 간 주의 신호 일치.",options:{bullet:true,breakLine:true}},{text:"‘긴축→검색’ 부호가 구글에서도 동일(예금·물가는 오히려 강화) — 핵심 결과 재현.",options:{bullet:true,breakLine:true}},{text:"부동산·투자는 플랫폼 간 이질성 존재(채널 특이성).",options:{bullet:true,breakLine:true}},{text:"→ 단일 자료의 우연이 아닌 외적 타당성(external validity) 확보.",options:{color:ACC,bold:true}}],{x:8.65,y:2.55,w:3.65,h:3.3,fontFace:F,fontSize:11.5,color:BODY,lineSpacingMultiple:1.15});
s.addText("참고문헌: 검색량을 시민 ‘주의’의 대리변수로 사용(OECD·Google Trends 경제활동 추적 연구) · 보도 논조 채널(Lamla & Lein, 「미디어와 소비자 인플레 기대」).",{x:MX,y:6.25,w:W-2*MX,h:0.35,fontFace:F,fontSize:9.5,italic:true,color:FAINT,margin:0});

// 11 결과 설명 ①
s=p.addSlide(); head(s,"결과 설명 ①",11,"주의–행동의 시차 분리 — 검색(attention) ≠ 실현행동");
box(s,MX,1.55,W-2*MX,0.72);
s.addText("마이닝 결과를 종합하면, 시민의 ‘주의(검색)’와 ‘실현행동(주택가격·가계대출 등)’은 정책에 상이한 속도로 반응한다. 아래는 긴축 어조와 실현행동 증가율의 시차 교차상관으로, 음(−)일수록 이론 정합(긴축 후 둔화·하락)을 뜻한다.",{x:MX+0.3,y:1.55,w:W-2*MX-0.6,h:0.72,fontFace:F,fontSize:12.5,color:BODY,valign:"middle",lineSpacingMultiple:1.15});
s.addChart(p.charts.LINE,[{name:"주택가격",labels:["0","3","6","9","12"],values:[0.28,0.14,-0.06,-0.26,-0.47]},{name:"가계대출",labels:["0","3","6","9","12"],values:[-0.04,-0.13,-0.27,-0.40,-0.49]},{name:"예금",labels:["0","3","6","9","12"],values:[-0.11,-0.23,-0.38,-0.46,-0.50]},{name:"예탁금",labels:["0","3","6","9","12"],values:[-0.13,-0.39,-0.62,-0.73,-0.76]}],{x:MX,y:2.5,w:7.5,h:3.85,chartColors:[RED,ACC,TEAL,AMBER],lineSize:2.25,lineSmooth:true,showLegend:true,legendPos:"b",legendFontFace:F,legendFontSize:11,catAxisTitle:"시차(개월, 정책 선행)",showCatAxisTitle:true,catAxisTitleFontFace:F,catAxisTitleFontSize:10.5,catAxisLabelFontFace:F,valAxisLabelFontFace:F,catAxisLabelColor:MUT,valAxisLabelColor:MUT,valGridLine:{color:HAIR,size:0.5},catGridLine:{style:"none"}});
box(s,8.4,2.5,W-MX-8.4,3.85);
s.addText([{text:"주의(검색)",options:{bold:true,color:HEAD,fontSize:13,breakLine:true}},{text:"정책 직후 수일 내 즉각 상승(사건연구) — 불안·정보탐색 성격.",options:{breakLine:true,color:BODY}},{text:" ",options:{breakLine:true,fontSize:6}},{text:"실현행동(주택가격·대출)",options:{bold:true,color:HEAD,fontSize:13,breakLine:true}},{text:"6–12개월 시차로 이론대로 둔화·하락(상관 음전환).",options:{breakLine:true,color:BODY}},{text:" ",options:{breakLine:true,fontSize:6}},{text:"∴ 긴축기 대출·부동산 검색 증가의 ‘겉보기 역설’은 빠른 주의와 느린 행동의 시간 분리로 설명된다.",options:{color:ACC,bold:true}}],{x:8.65,y:2.7,w:3.65,h:3.5,fontFace:F,fontSize:11.5,color:BODY,lineSpacingMultiple:1.13});

// 12 결과 설명 ②
s=p.addSlide(); head(s,"결과 설명 ②",12,"정보 반응 속도의 위계 — 시장(선반영)·주의·행동");
box(s,MX,1.55,W-2*MX,0.7);
s.addText("반응 주체를 금융시장·시민 주의·시민 행동으로 구분하면, 정책 충격이 거시→미시로 ‘속도의 위계’를 따라 전달된다. 시장 사건연구에서 결정일 비정상 변동이 관측되지 않은 것은, 정기 결정이 대체로 예견되어 시장이 사전 반영(price discovery)했기 때문이다.",{x:MX+0.3,y:1.55,w:W-2*MX-0.6,h:0.7,fontFace:F,fontSize:12.5,color:BODY,valign:"middle",lineSpacingMultiple:1.15});
s.addTable([[th("반응 계층"),th("반응 속도"),th("내용 / 근거")],
 ["① 금융시장 (환율·KOSPI)","즉시 · 선반영","결정일 비정상 변동 미관측. 정기 결정 예견 → 정보 효율적 사전 반영(환율 |Δ| 0.34% ≈ 평소)."],
 ["② 시민 주의 (검색)","수일","결정 직후 1주 예금 +17%(매파 시 +25%), 며칠 내 급등 후 정상화."],
 ["③ 시민 행동 (주택가격·대출)","수개월","6–12개월 시차로 이론 정합적 둔화·하락. 최후행 계층."]],
 {x:MX,y:2.45,w:W-2*MX,colW:[3.7,2.0,6.63],rowH:0.82,fontFace:F,fontSize:12.5,color:BODY,valign:"middle",border:{type:"solid",pt:0.5,color:HAIR}});
box(s,MX,5.45,W-2*MX,1.0);
s.addText([{text:"종합   ",options:{bold:true,color:ACC,fontSize:13.5}},{text:"전문 시장은 정책을 선반영하고, 일반 시민은 사후에 주의를 보이며, 실현행동은 가장 느리게 따라온다. ‘시민이 정책을 따른다’는 사실의 확인이 아니라, 누가·언제·어떤 경로로 반응하는지의 구조가 본 연구의 발견이다.",options:{color:BODY}}],{x:MX+0.3,y:5.45,w:W-2*MX-0.6,h:1.0,fontFace:F,fontSize:12.5,valign:"middle",lineSpacingMultiple:1.18});

// 13 활용
s=p.addSlide(); head(s,"활용방안 제시",13,"정책 타이밍 × 인구통계 타겟 — 금융상품 마케팅 의사결정");
box(s,MX,1.55,W-2*MX,0.6);
s.addText("분석 결과는 금융기관 상품 마케팅 의사결정에 활용 가능하다. (좌) 정책기조별 사건 직후 검색 리프트로 ‘마케팅 적기’를, (우) 인구통계 세분화로 ‘타겟 연령’을 도출한다.",{x:MX+0.3,y:1.55,w:W-2*MX-0.6,h:0.6,fontFace:F,fontSize:12.5,color:BODY,valign:"middle"});
s.addText("정책 결정 직후 1주 검색 리프트 (%)",{x:MX,y:2.4,w:6,h:0.32,fontFace:F,fontSize:12,bold:true,color:HEAD,margin:0});
s.addTable([[th("상품축"),th("매파(긴축) 후"),th("비둘기(완화) 후")],["예금","+24.8%","+4.4%"],["대출","−0.2%","+12.4%"],["환율","−3.3%","+5.4%"],["물가","+5.2%","+3.4%"],["투자","−4.4%","+3.2%"]],{x:MX,y:2.78,w:6.0,h:2.55,colW:[1.6,2.2,2.2],rowH:0.43,fontFace:F,fontSize:12,color:BODY,valign:"middle",align:"center",border:{type:"solid",pt:0.5,color:HAIR}});
box(s,MX,5.5,6.0,0.95);
s.addText("→ 매파 결정 직후 = 예·적금, 비둘기 직후 = 대출 상품 마케팅 적기.",{x:MX+0.25,y:5.5,w:5.5,h:0.95,fontFace:F,fontSize:12,bold:true,color:ACC,valign:"middle",margin:0,lineSpacingMultiple:1.1});
s.addText("연령별 평균 검색지수 (타겟 도출)",{x:6.85,y:2.4,w:5,h:0.32,fontFace:F,fontSize:12,bold:true,color:HEAD,margin:0});
s.addTable([[th("축"),th("청년 19-34"),th("중년 35-54"),th("장년 55+")],["예금","15.2","9.0","8.0"],["대출","52.3","48.3","37.6"],["부동산","69.9","63.0","42.7"],["물가","26.0","18.6","15.3"]],{x:6.85,y:2.78,w:5.98,h:2.1,colW:[1.18,1.7,1.6,1.5],rowH:0.42,fontFace:F,fontSize:11.5,color:BODY,valign:"middle",align:"center",border:{type:"solid",pt:0.5,color:HAIR}});
box(s,6.85,5.05,5.98,1.4);
s.addText("→ 금융 관심의 주역은 청년층(19-34). ‘긴축기 예금 관심 급증’의 핵심 타겟은 청년.",{x:7.1,y:5.05,w:5.5,h:1.4,fontFace:F,fontSize:12,bold:true,color:ACC,valign:"middle",margin:0,lineSpacingMultiple:1.15});

// 14 결론
s=p.addSlide(); head(s,"결론",14);
box(s,MX,1.15,W-2*MX,0.95);
s.addText("본 연구는 정책 어조를 수치화하고 시민의 검색·실현행동·보도·시장 자료와 결합하여 정책–시민 반응 구조를 다중 기법으로 분석하였다. ‘정책대로 시민이 움직인다’는 방향의 확인을 넘어, 비교정태가 비워둔 ‘속도·순서·주체·이탈’을 자료로 규명한 점이 기여이다.",{x:MX+0.3,y:1.15,w:W-2*MX-0.6,h:0.95,fontFace:F,fontSize:12.5,color:BODY,valign:"middle",lineSpacingMultiple:1.18});
box(s,MX,2.25,W-2*MX,2.35);
s.addText([{text:"주요 발견",options:{bold:true,color:ACC,fontSize:13.5,breakLine:true}},{text:"주의는 정책 직후 수일 내 즉각, 실현행동은 6–12개월 시차로 반응 — 검색 ≠ 행동의 시간 분리.",options:{bullet:true,breakLine:true}},{text:"정보 속도의 위계: 시장 선반영 → 시민 주의(사후) → 실현행동(최후). 시민은 보도를 매개로(약 4일 선행) 반응.",options:{bullet:true,breakLine:true}},{text:"정책–시민 관계를 6개 잠재국면으로 유형화, 이론 이탈 시점은 외생충격으로 해석. 네이버·구글·유튜브에서 재현.",options:{bullet:true,breakLine:true}},{text:"활용: 매파 직후 예·적금, 비둘기 직후 대출, 타겟 청년층 — 분석을 의사결정 도구로 전환.",options:{bullet:true}}],{x:MX+0.3,y:2.4,w:W-2*MX-0.6,h:2.1,fontFace:F,fontSize:12,color:BODY,lineSpacingMultiple:1.18});
box(s,MX,4.75,W-2*MX,1.7);
s.addText([{text:"연구의 한계 및 향후 과제",options:{bold:true,color:HEAD,fontSize:13.5,breakLine:true}},{text:"검색은 ‘주의’의 대리변수로 실제 수요와 상이할 수 있으며, 가계대출은 총대출금 대용치 사용. 정기 결정의 시장 무반응은 정책 서프라이즈를 분리하지 못한 데 기인. 표본 108개월의 탐색적 사례연구로 포지셔닝.",options:{bullet:true,breakLine:true}},{text:"향후: 정책 서프라이즈 분리, 순수 가계대출·주택 거래량 결합, 어조 라벨 골든셋 검증, 보도 본문 기반 프레이밍 분석.",options:{bullet:true}}],{x:MX+0.3,y:4.9,w:W-2*MX-0.6,h:1.45,fontFace:F,fontSize:11.5,color:BODY,lineSpacingMultiple:1.18});
s.addText("표본 n=108개월의 탐색적 사례연구로 포지셔닝(순위기반·robust 기법 우선, 유의성 병기). 전체 방법론·출처는 프로젝트 METHODOLOGY.md·REFERENCES.md 참조.",{x:MX,y:6.55,w:W-2*MX,h:0.35,fontFace:F,fontSize:9.5,italic:true,color:FAINT,margin:0});

// (부록 ①②는 각 분석 슬라이드 하단 각주로 통합 — 표지~결론 14p)

p.writeFile({fileName:PR+"/정책_시민반응_결과보고서.pptx"}).then(f=>console.log("OK",f));
