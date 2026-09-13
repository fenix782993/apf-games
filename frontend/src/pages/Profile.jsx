import React,{useEffect,useState} from "react";
import {api} from "../lib/api";
export default function Profile({user}){
 const [history,setHistory]=useState([]),[ach,setAch]=useState([]),[task,setTask]=useState(null);
 useEffect(()=>{Promise.all([api("/api/games/history"),api("/api/achievements"),api("/api/tasks/daily")]).then(([h,a,t])=>{setHistory(h);setAch(a);setTask(t[0])}).catch(()=>{})},[]);
 const claim=async()=>{await api("/api/tasks/daily/claim",{method:"POST"});location.reload()};
 return <section className="panel"><div className="profileTop"><div className="avatar">{user.name[0]?.toUpperCase()}</div><div><h1>{user.name}</h1><p>{user.email}</p></div></div><div className="stats"><div><b>{user.level}</b><small>Уровень</small></div><div><b>{user.xp}</b><small>XP</small></div><div><b>{user.points}</b><small>APF Points</small></div><div><b>{user.games_played}</b><small>Игр</small></div></div>{task&&<div className="task"><div><b>Ежедневное задание</b><p>Сыграть 3 игры · {task.progress}/{task.target}</p></div>{task.progress>=task.target&&!task.claimed&&<button className="primary" onClick={claim}>ЗАБРАТЬ +100</button>}</div>}<h2>Достижения</h2><div className="achievementGrid">{ach.map(a=><div className="achievement" key={a.code}>🏆 <b>{a.title}</b></div>)}</div><h2>История</h2>{history.map((r,i)=><div className="history" key={i}><span>{r.game}</span><b>{r.score}</b><small>+{r.xp} XP</small></div>)}</section>
}
