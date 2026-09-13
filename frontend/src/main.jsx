import React,{useEffect,useState} from "react";
import {createRoot} from "react-dom/client";
import {Gamepad2,Trophy,UserRound,LogOut,ArrowLeft,Shield} from "lucide-react";
import {api} from "./lib/api";
import Auth from "./pages/Auth";
import Profile from "./pages/Profile";
import GameCard from "./components/GameCard";
import Race from "./games/Race";
import Parking from "./games/Parking";
import Quiz from "./games/Quiz";
import Memory from "./games/Memory";
import "./styles.css";

const games=[
 {id:"race",name:"APF Race",icon:"🏎️",description:"Разгоняй машину и удерживай скорость 20 секунд."},
 {id:"parking",name:"Perfect Parking",icon:"🅿️",description:"Припаркуйся точно в зоне с минимальным числом ходов."},
 {id:"quiz",name:"Auto Quiz",icon:"🧠",description:"Проверь свои знания автомобилей."},
 {id:"memory",name:"Auto Memory",icon:"🧩",description:"Найди все автомобильные пары."}
];

function App(){
 const [user,setUser]=useState(null),[tab,setTab]=useState("games"),[game,setGame]=useState(null),[result,setResult]=useState(null),[leader,setLeader]=useState([]),[leaderGame,setLeaderGame]=useState("race");
 useEffect(()=>{if(localStorage.getItem("apf_token"))api("/api/me").then(setUser).catch(()=>localStorage.removeItem("apf_token"))},[]);
 useEffect(()=>{if(tab==="rating")api("/api/games/leaderboard/"+leaderGame).then(setLeader).catch(()=>setLeader([]))},[tab,leaderGame]);
 if(!user)return <Auth onAuth={setUser}/>;
 const finish=async score=>{const d=await api("/api/games/result",{method:"POST",body:JSON.stringify({game,score,duration:0})});setResult(d);const fresh=await api("/api/me");setUser(fresh)};
 const logout=()=>{localStorage.removeItem("apf_token");setUser(null)};
 return <div className="app">
  <header><div className="brand">APF <span>GAMES</span></div><nav><button className={tab==="games"?"active":""} onClick={()=>{setTab("games");setGame(null)}}><Gamepad2/> Игры</button><button className={tab==="rating"?"active":""} onClick={()=>setTab("rating")}><Trophy/> Рейтинг</button><button className={tab==="profile"?"active":""} onClick={()=>setTab("profile")}><UserRound/> Профиль</button></nav><button className="logout" onClick={logout}><LogOut/></button></header>
  <main>
   {tab==="games"&&!game&&<><section className="hero"><div><label>APF ENTERTAINMENT</label><h1>Играй.<br/>Зарабатывай XP.<br/>Попадай в топ.</h1><p>Реальные игровые механики, сохранение результатов, достижения, задания и рейтинг.</p></div><div className="heroEmoji">🏁</div></section><div className="grid">{games.map(g=><GameCard game={g} onClick={()=>{setGame(g.id);setResult(null)}} key={g.id}/>)}</div></>}
   {tab==="games"&&game&&<section><button className="back" onClick={()=>setGame(null)}><ArrowLeft/> Все игры</button><div className="panel"><div className="gameTitle"><span>{games.find(x=>x.id===game)?.icon}</span><h1>{games.find(x=>x.id===game)?.name}</h1></div>{game==="race"&&<Race onFinish={finish}/>} {game==="parking"&&<Parking onFinish={finish}/>} {game==="quiz"&&<Quiz onFinish={finish}/>} {game==="memory"&&<Memory onFinish={finish}/>} </div>{result&&<div className="result"><b>Игра завершена</b><span>Счёт {result.score}</span><span>+{result.xp} XP</span><span>+{result.points} APF Points</span><button className="primary" onClick={()=>{setResult(null);setGame(null)}}>К ИГРАМ</button></div>}</section>}
   {tab==="rating"&&<section className="panel"><div className="sectionHead"><h1>Рейтинг</h1><select value={leaderGame} onChange={e=>setLeaderGame(e.target.value)}>{games.map(g=><option value={g.id} key={g.id}>{g.name}</option>)}</select></div>{leader.map(r=><div className="rank" key={r.rank}><b>#{r.rank}</b><span>{r.name}</span><strong>{r.score}</strong></div>)}{!leader.length&&<p className="muted">Пока никто не играл. Будь первым.</p>}</section>}
   {tab==="profile"&&<Profile user={user}/>}
  </main>
 </div>
}
createRoot(document.getElementById("root")).render(<App/>);
