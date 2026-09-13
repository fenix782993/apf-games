import React,{useEffect,useState} from "react";
const symbols=["🚗","🏎️","🚕","🚙","🛻","🚓","🚗","🏎️","🚕","🚙","🛻","🚓"];
export default function Memory({onFinish}){
 const [cards,setCards]=useState([]),[open,setOpen]=useState([]),[matched,setMatched]=useState([]),[moves,setMoves]=useState(0),[started,setStarted]=useState(false);
 const start=()=>{setCards([...symbols].sort(()=>Math.random()-.5));setOpen([]);setMatched([]);setMoves(0);setStarted(true)};
 useEffect(()=>{
   if(open.length!==2)return;
   const [a,b]=open;
   setMoves(m=>m+1);
   const t=setTimeout(()=>{
     if(cards[a]!==cards[b])setOpen([]);
     else {setMatched(m=>[...m,a,b]);setOpen([])}
   },550);
   return()=>clearTimeout(t);
 },[open]);
 useEffect(()=>{if(started&&matched.length===cards.length){setStarted(false);onFinish(Math.max(100,1800-moves*70))}},[matched]);
 if(!started)return <div className="emptyGame"><h2>Auto Memory</h2><p>Найди все пары. Чем меньше ходов — тем выше счёт.</p><button className="primary" onClick={start}>НАЧАТЬ</button></div>;
 return <div className="game"><div className="memory">{cards.map((c,i)=>{let visible=open.includes(i)||matched.includes(i);return <button key={i} className={"memoryCard "+(visible?"visible":"")} onClick={()=>visible||open.length>=2?null:setOpen([...open,i])}>{visible?c:"?"}</button>})}</div><div className="muted">Ходы: {moves}</div></div>
}
