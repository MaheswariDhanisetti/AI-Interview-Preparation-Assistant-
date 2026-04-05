const express = require("express")
const cookieParser = require("cookie-parser")
const cors = require("cors")

const app = express()
const allowedOrigins = (process.env.CORS_ORIGINS || "http://localhost:5173")
    .split(",")
    .map((origin) => origin.trim())
    .filter(Boolean)

app.use(express.json())
app.use(cookieParser())
app.use(cors({
    origin: allowedOrigins,
    credentials: true
}))

app.get("/api/health", (req, res) => {
    res.status(200).json({ status: "ok" })
})

/* require all the routes here */
const authRouter = require("./routes/auth.routes")
const interviewRouter = require("./routes/interview.routes")


/* using all the routes here */
app.use("/api/auth", authRouter)
app.use("/api/interview", interviewRouter)

app.use((err, req, res, next) => {
    console.error(err)
    res.status(err.statusCode || 500).json({
        message: err.message || "Internal server error"
    })
})


module.exports = app