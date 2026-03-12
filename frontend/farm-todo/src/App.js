import { useEffect,useState } from "react";
import axios from "axios";
import "./App.css";
import ListToDoLists from "./ListTodoLists";
import ToDoList from "./ToDoList";

function App() {
  const [listSummaries, setListSummaries] = useState(null);
  const [seletedItem, setSelectedItem] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() =>{
    reloadData().catch(err => {
      console.error(err);
      setError("Failed to load to-do lists. Check your backend connection.");
    });
  },[]);

  async function reloadData(){
    setError(null);
    const response = await axios.get("/api/lists");
    setListSummaries(response.data);
  }

  function handleNewToDoList(nameName){
    const updateData = async () => {
      const newListData = {
        name: nameName,
      };

      await axios.post(`/api/lists`, newListData);
      reloadData().catch(console.error);
    };
    updateData();
  }

  function handleDeleteToDoList(id) {
    const updateData =async () =>{
      await axios.delete(`/api/lists/${id}`);
      reloadData().catch(console.error);
    };
    updateData();
  }

  function handleSelectList(id) {
    console.log("Selecting item", id);
    setSelectedItem(id);
  }
  
  function backToLists() {
    setSelectedItem(null);
    reloadData().catch(console.error);
  }

  if (error) {
    return (
      <div className="App">
        <div className="error-message">
           <h2>Connectivity Issue</h2>
           <p>{error}</p>
           <button onClick={() => reloadData()}>Retry Connection</button>
        </div>
      </div>
    );
  }

  if (listSummaries === null) {
    return (
      <div className="App">
        <div className="loading">
          <div className="spinner"></div>
          <p>Connecting to your personal task board...</p>
        </div>
      </div>
    );
  }

  if (seletedItem === null) {
    return (
      <div className="App">
        <ListToDoLists
          listSummaries={listSummaries}
          handleSelectList={handleSelectList}
          handleNewToDoList={handleNewToDoList}
          handleDeleteToDoList={handleDeleteToDoList}
        />
      </div>
    );
  } else {
    return (
      <div className="App">
        <ToDoList
          listId={seletedItem}
          backToLists={backToLists}
        />
      </div>
    );
  }
}

export default App;
  


  
