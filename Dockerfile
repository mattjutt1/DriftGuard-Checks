# Simple test server for Railway to verify it works
FROM node:18-slim

RUN echo 'const express = require("express");\n\
const app = express();\n\
const PORT = process.env.PORT || 3000;\n\
\n\
console.log("Starting test server on port", PORT);\n\
\n\
app.get("/api/tags", (req, res) => {\n\
  console.log("Health check hit!");\n\
  res.json({\n\
    models: [{\n\
      name: "qwen3:4b",\n\
      size: 2600000000,\n\
      modified_at: new Date().toISOString()\n\
    }]\n\
  });\n\
});\n\
\n\
app.get("/api/generate", (req, res) => {\n\
  console.log("Generate request:", req.body?.prompt?.substring(0, 50));\n\
  res.json({\n\
    model: "qwen3:4b",\n\
    response: "This is a mock response from the Railway test server. The real Ollama deployment will replace this.",\n\
    done: true\n\
  });\n\
});\n\
\n\
app.listen(PORT, "0.0.0.0", () => {\n\
  console.log(`Railway test server running on port ${PORT}`);\n\
});\n\
' > server.js

RUN npm init -y && npm install express

CMD ["node", "server.js"]