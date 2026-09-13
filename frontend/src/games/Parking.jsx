import React,{useState} from "react";
export default function Parking({onFinish}){
 const [x,setX]=useState(5),[moves,setMoves]=useState(0),[active,setActive]=useState(false);
 const start=()=>{setX(5);setMoves(0);setActive(true)};
 const move=d=>{
   if(!active)return;
   const nx=Math.max(0,Math.min(95,x+d)); const nm=moves+1;
   setX(nx);setMoves(nm);
   if(nx>=78&&nx<=88){setActive(false);onFinish(Math.max(100,1200-nm*80))}
   else if(nm>=12){setActive(false);onFinish(0)}
 };
 return <div className="game">
   <div className="parkingBoard"><div className="parkingZone">P</div><div className="parkingCar" style={{left:`${x}%`}}>🚗</div></div>
   <div className="gameStats"><span>Позиция {x}%</span><span>Ходы {moves}/12</span></div>
   <div className="controls"><button className="primary" onClick={start}>НОВАЯ ИГРА</button><button className="secondary" onClick={()=>move(7)}>ВПЕРЁД</button><button className="secondary" onClick={()=>move(-7)}>НАЗАД</button></div>
 </div>
}
