require("dotenv").config()
const app = require("./src/app")
const connectToDB = require("./src/config/database")

const port = Number(process.env.PORT || 3000)

if (!process.env.JWT_SECRET) {
    throw new Error("JWT_SECRET is missing in Backend/.env")
}

if (!process.env.MONGO_URI) {
    throw new Error("MONGO_URI is missing in Backend/.env")
}

connectToDB()


app.listen(port, () => {
    console.log(`Server is running on port ${port}`)
})