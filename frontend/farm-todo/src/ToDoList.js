import { useState, useEffect } from "react";
import axios from "axios";
import { BiArrowBack, BiPlus, BiCheckCircle, BiCircle } from "react-icons/bi";
import "./ToDoList.css";

function ToDoList({ listId, backToLists }) {
    const [items, setItems] = useState(null);
    const [newItemContent, setNewItemContent] = useState("");

    useEffect(() => {
        loadItems();
    }, [listId]);

    const loadItems = async () => {
        try {
            const response = await axios.get(`/api/lists/${listId}/items`);
            setItems(response.data);
        } catch (error) {
            console.error("Error loading items:", error);
        }
    };

    const handleAddItem = async () => {
        if (!newItemContent.trim()) return;
        try {
            await axios.post(`/api/lists/${listId}/items`, { content: newItemContent });
            setNewItemContent("");
            loadItems();
        } catch (error) {
            console.error("Error adding item:", error);
        }
    };

    const handleToggleItem = async (item) => {
        try {
            await axios.put(`/api/items/${item.id}`, { completed: !item.completed });
            loadItems();
        } catch (error) {
            console.error("Error toggling item:", error);
        }
    };

    if (items === null) return <div className="loading">Loading tasks...</div>;

    return (
        <div className="ToDoList">
            <button className="back" onClick={backToLists}>
                <BiArrowBack /> Back to Boards
            </button>
            
            <h1>Board Tasks</h1>
            
            <div className="box">
                <input 
                    type="text" 
                    value={newItemContent} 
                    onChange={(e) => setNewItemContent(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleAddItem()}
                    placeholder="What needs to be done?"
                />
                <button onClick={handleAddItem}>
                    <BiPlus size={20} /> Add
                </button>
            </div>

            {items.length === 0 ? (
                <div className="empty-state">
                    <p>No tasks yet. Add your first task to get started!</p>
                </div>
            ) : (
                items.map(item => (
                    <div 
                        key={item.id} 
                        className={`item ${item.completed ? 'checked' : ''}`}
                        onClick={() => handleToggleItem(item)}
                    >
                        {item.completed ? (
                            <BiCheckCircle size={24} color="#6366f1" />
                        ) : (
                            <BiCircle size={24} color="#94a3b8" />
                        )}
                        <span className="label">{item.content}</span>
                    </div>
                ))
            )}
        </div>
    );
}

export default ToDoList;
