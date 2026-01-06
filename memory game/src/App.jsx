
import { GameHeader } from "./components/gameheader";
import Card from "./components/Card";
import { useState } from "react";
const cardValues = [
  "🍎",
  "🍌",
  "🍇",
  "🍊",
  "🍓",
  "🥝",
  "🍑",
  "🍒",
  "🍎",
  "🍌",
  "🍇",
  "🍊",
  "🍓",
  "🥝",
  "🍑",
  "🍒",
];

function App() {
  //card is flipped or not
  const [cards,setCards]=useState([])
  const initialiseGame=()=>{
     //shuffle the cards
    console.log(cardValues)
    const finalCards= cardValues.map((value,index)=>({
          id:index,
          value,
          isFlipped:false,
          isMatched:false,
      })); 
  setCards(finalCards)
  }
  return (
    <div className="app">
      <GameHeader score={3} moves={10}/>
      <div className="cards-grid">
        {cardValues.map((card)=>(
               <Card card={card}/>
        ))}
      </div>
    </div>
  )
}

export default App;
