import React from "react";
export default function GameCard({game,onClick}){
 return <button className="gameCard" onClick={onClick}>
   <div className="gameEmoji">{game.icon}</div><h3>{game.name}</h3><p>{game.description}</p><span>Играть →</span>
 </button>
}
