
import { GameHeader } from "./components/GameHeader";
import {Card} from "./components/Card";
import { useState,useEffect } from "react";
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
  setCards(finalCards);
  }
  useEffect(()=>{
    initialiseGame();
  },
    []);
    const handleCardClick=(card)=>{
      if(card.isFlipped||card.isMatched){
        return;
      }
      //Update card flip state
      const newCards=cards.map((c)=>{
        if(c.id==card.id){
          return{...c,isFlipped:true};
        }else{
          return c
        }
      })
      setCards(newCards);
    }
  return (
    <div className="app">
      <GameHeader score={3} moves={10}/>
      <div className="cards-grid">
        {cards.map((card)=>(
               <Card card={card} onClick={handleCardClick}/>
        ))}
      </div>
    </div>
  )
}

export default App;
