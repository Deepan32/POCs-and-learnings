import { useState } from "react";

function App() {
  // Local state for input text
  const [taskText, setTaskText] = useState("");
  const [theme,setTheme]=useState("light");
  //taskText ---> input value
  //setTaskText ---> input function
  //Argument for useState is the initial value of state variable
  return (
    <div style={{ minHeight : "100vh",
      color: theme === "dark" ? "#ffffff" : "#213547",
      backgroundColor: theme==="light" ? "#ffffff" : "#213547",
     }}>
      <h2>Smart Task Dashboard</h2>
      {/*Theme Toggle Button*/}
      <button onClick={() => setTheme(theme === "light" ? "dark" : "light")}>Change Theme</button><br/>
      {/* Controll Input */}
      <input
        type="text"
        placeholder="Enter a task"
        value={taskText}
        onChange={(e) => setTaskText(e.target.value)}
      />
      {/*e means event target mean where the event happened here <input> value means what is typed  */}
      {/* Just to verify state */}
      <p>You typed: {taskText}</p>
    </div>
  );
}

export default App;
