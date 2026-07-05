#!/usr/bin/env python3
"""Simple MySQL MCP server for Hermes Agent."""
import json
import sys
import mysql.connector

def handle_request(req):
    method = req.get("method", "")
    req_id = req.get("id")
    
    if method == "initialize":
        return {"jsonrpc": "2.0", "id": req_id, "result": {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "mysql-mcp", "version": "1.0.0"}
        }}
    
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": [
            {
                "name": "mysql_query",
                "description": "Execute a SELECT query on the MySQL database. Use for reading data only.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "SQL SELECT query to execute"}
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "mysql_show_tables",
                "description": "List all tables in the database.",
                "inputSchema": {"type": "object", "properties": {}}
            },
            {
                "name": "mysql_describe_table",
                "description": "Show the schema of a specific table.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "table": {"type": "string", "description": "Table name"}
                    },
                    "required": ["table"]
                }
            }
        ]}}
    
    if method == "tools/call":
        tool_name = req["params"]["name"]
        args = req["params"].get("arguments", {})
        
        try:
            conn = mysql.connector.connect(
                host="rf-hacks.com",
                port=3306,
                user="rfhacks_user",
                password="rfhacks_pass_2024",
                database="rfhacks_test_db",
                connect_timeout=10
            )
            cursor = conn.cursor(dictionary=True)
            
            if tool_name == "mysql_query":
                query = args["query"]
                if not query.strip().upper().startswith("SELECT"):
                    return {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": "Error: Only SELECT queries allowed"}]}}
                cursor.execute(query)
                rows = cursor.fetchall()
                text = json.dumps(rows, default=str, indent=2) if rows else "(empty result)"
                
            elif tool_name == "mysql_show_tables":
                cursor.execute("SHOW TABLES")
                rows = cursor.fetchall()
                text = "\n".join(list(r.values())[0] for r in rows) if rows else "(no tables)"
                
            elif tool_name == "mysql_describe_table":
                cursor.execute(f"DESCRIBE {args['table']}")
                rows = cursor.fetchall()
                text = json.dumps(rows, default=str, indent=2)
            
            cursor.close()
            conn.close()
            
            return {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": text}]}}
            
        except Exception as e:
            return {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": f"Error: {e}"}]}}
    
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Unknown method: {method}"}}

def main():
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            req = json.loads(line.strip())
            resp = handle_request(req)
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()
        except json.JSONDecodeError:
            continue
        except BrokenPipeError:
            break

if __name__ == "__main__":
    main()
