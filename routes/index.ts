import express from 'express'
import cors from 'cors'
import clientesRoutes from './clientes'
import emailRoutes from './email'
import vendasRoutes from './vendas'
import vendedorasRoutes from './vendedoras'


const app = express()
const port = process.env.PORT || 10000

app.use(express.json())
app.use(cors())

app.use("/clientes", clientesRoutes)
app.use("/email", emailRoutes)
app.use("/vendas", vendasRoutes)
app.use("/vendedoras", vendedorasRoutes)

app.get('/', (req, res) => {
  res.send('API: Convertix - Backend')
})

app.listen(port, () => {
  console.log(`Servidor rodando na porta: ${port}`)
})
console.log('PORT lida do .env:', process.env.PORT);