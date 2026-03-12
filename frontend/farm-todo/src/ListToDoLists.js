import "./ListTodoLists.css";
import { useRef } from "react";
import { BiSolidTrash, BiPlus } from "react-icons/bi";

function ListToDoLists({
    listSummaries,
    handleSelectList,
    handleNewToDoList,
    handleDeleteToDoList
}) {
    const labelRef = useRef();

    const onNewList = () => {
        if (labelRef.current && labelRef.current.value.trim()) {
            handleNewToDoList(labelRef.current.value.trim());
            labelRef.current.value = "";
        }
    };

    return (
        <div className="ListToDoLists">
            <h1>Farm To-Do Lists</h1>
            
            <div className="box">
                <input 
                    ref={labelRef} 
                    type="text" 
                    placeholder="Create a new task list..."
                    onKeyPress={(e) => e.key === 'Enter' && onNewList()}
                />
                <button onClick={onNewList}>
                    <BiPlus size={20} />
                    Create
                </button>
            </div>

            {listSummaries.length === 0 ? (
                <div className="empty-state">
                    <p>Your task boards are currently empty. Start by creating one above!</p>
                </div>
            ) : (
                listSummaries.map((summary) => (
                    <div
                        key={summary.id}
                        className="summary"
                        onClick={() => handleSelectList(summary.id)}
                    >
                        <div className="name">{summary.name}</div>
                        <div className="count">{summary.item_count} tasks</div>
                        <div className="flex"></div>
                        <div
                            className="trash"
                            onClick={(evt) => {
                                evt.stopPropagation();
                                if(window.confirm("Delete this list?")) {
                                    handleDeleteToDoList(summary.id);
                                }
                            }}
                        >
                            <BiSolidTrash size={20} />
                        </div>
                    </div>
                ))
            )}
        </div>
    );
}

export default ListToDoLists;
