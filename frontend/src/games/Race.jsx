import React,{useEffect,useState} from "react";
import {Play,Square} from "lucide-react";

export default function Race({onFinish}){
 const [running,setRunning]=useState(false),[time,setTime]=useState(20),[speed,setSpeed]=useState(0),[score,setScore]=useState(0),[distance,setDistance]=useState(0);
 useEffect(()=>{
   if(!running)return;
   if(time<=0){setRunning(false);onFinish(score);return}
   const id=setInterval(()=>{
     setTime(t=>t-1);
     setSpeed(s=>Math.max(0,s-10));
     setDistance(d=>d+speed/4);
     setScore(s=>s+Math.floor(speed/8));
   },1000);
   return()=>clearInterval(id);
 },[running,time,speed,score]);
 const start=()=>{setTime(20);setSpeed(0);setScore(0);setDistance(0);setRunning(true)};
 return <div className="game">
   <div className="gameStats"><b>{time}s</b><span>Скорость {speed} км/ч</span><span>Очки {score}</span></div>
   <div className="raceRoad"><div className="lane"></div><div className="raceCar" style={{transform:`translateX(${Math.min(55,distance)}%)`}}>🏎️</div></div>
   <div className="controls">
     <button className="primary" onClick={start}><Play/> {running?"ЗАНОВО":"СТАРТ"}</button>
     <button className="secondary" disabled={!running} onClick={()=>{setSpeed(s=>Math.min(320,s+40));setScore(s=>s+30)}}>ГАЗ</button>
     <button className="secondary" disabled={!running} onClick={()=>setSpeed(s=>Math.max(0,s-70))}><Square/> ТОРМОЗ</button>
   </div>
 </div>
}
