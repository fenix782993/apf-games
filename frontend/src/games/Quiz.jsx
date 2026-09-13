import React,{useState} from "react";
const questions=[
 ["Какая марка выпускает Mustang?","Ford",["Ford","BMW","Audi","Kia"]],
 ["Как называется полный привод Audi?","quattro",["xDrive","quattro","4MOTION","AWD"]],
 ["Что измеряют в лошадиных силах?","мощность",["массу","мощность","объём","давление"]],
 ["Что означает ABS?","антиблокировка тормозов",["антиблокировка тормозов","турбонаддув","полный привод","круиз-контроль"]],
 ["Какой двигатель имеет цилиндры в V-образной схеме?","V6",["I4","V6","Wankel","H4"]]
];
export default function Quiz({onFinish}){
 const [i,setI]=useState(0),[score,setScore]=useState(0),[started,setStarted]=useState(false);
 const start=()=>{setI(0);setScore(0);setStarted(true)};
 const answer=a=>{
   const ns=score+(a===questions[i][1]?250:0);
   if(i===questions.length-1){setStarted(false);onFinish(ns)} else {setScore(ns);setI(i+1)}
 };
 if(!started)return <div className="emptyGame"><h2>Auto Quiz</h2><p>5 вопросов. За правильный ответ — 250 очков.</p><button className="primary" onClick={start}>НАЧАТЬ</button></div>;
 const q=questions[i];
 return <div className="game"><div className="question">{q[0]}</div><div className="answers">{q[2].map(a=><button key={a} onClick={()=>answer(a)}>{a}</button>)}</div><div className="muted">Вопрос {i+1} из {questions.length}</div></div>
}
