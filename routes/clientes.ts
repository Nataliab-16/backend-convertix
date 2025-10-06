import { PrismaClient } from "@prisma/client"
import { Router } from "express"
import bcrypt from 'bcrypt'
import { validaSenha } from "../../shared/functionValidaSenha"

const prisma = new PrismaClient()
const router = Router()

router.get("/", async (req, res) => {
  const email = req.query.email;
  if (typeof email !== 'string' || !email) {
    return res.status(400).json({ error: "Email deve ser uma string válida." });
  }
  try {
    const cliente = await prisma.cliente.findFirst({ where: { email: email } })
    res.status(200).json(cliente)
  } catch (error) {
    res.status(400).json(error)
  }
})



router.post("/", async (req, res) => {
  const { nome, email, senha } = req.body

  if (!nome || !email || !senha) {
    res.status(400).json({ erro: "Informe nome, email e senha" })
    return
  }

  const erros = validaSenha(senha)
  if (erros.length > 0) {
    res.status(400).json({ erro: erros.join("; ") })
    return
  }

  // 12 é o número de voltas (repetições) que o algoritmo faz
  // para gerar o salt (sal/tempero)
  const salt = bcrypt.genSaltSync(12)
  // gera o hash da senha acrescida do salt
  const hash = bcrypt.hashSync(senha, salt)

  // para o campo senha, atribui o hash gerado
  try {
    const cliente = await prisma.cliente.create({
      data: { nome, email, senha: hash }
    })
    res.status(201).json(cliente)
  } catch (error) {
    res.status(400).json(error)
  }
})


router.post("/login", async (req, res) => {
  const { email, senha } = req.body

  // em termos de segurança, o recomendado é exibir uma mensagem padrão
  // a fim de evitar de dar "dicas" sobre o processo de login para hackers
  const mensaPadrao = "Login ou senha incorretos"

  if (!email || !senha) {
    // res.status(400).json({ erro: "Informe e-mail e senha do usuário" })
    res.status(400).json({ erro: mensaPadrao })
    return
  }

  try {
    const cliente = await prisma.cliente.findUnique({
      where: { email }
    })

    if (cliente == null) {
      // res.status(400).json({ erro: "E-mail inválido" })
      res.status(400).json({ erro: mensaPadrao })
      return
    }

    // se o e-mail existe, faz-se a comparação dos hashs
    if (bcrypt.compareSync(senha, cliente.senha)) {

      res.status(200).json({
        id: cliente.id,
        nome: cliente.nome,
        email: cliente.email
      })
    } else {
      res.status(400).json({ erro: mensaPadrao })
    }
  } catch (error) {
    res.status(400).json(error)
  }
})


router.patch("/:id", async (req, res) => {
  const { id } = req.params
  const { senha } = req.body

  const salt = bcrypt.genSaltSync(12)
  const hash = bcrypt.hashSync(senha, salt)

  try {
    const cliente = await prisma.cliente.update({
      where: { id: String(id) },
      data: { senha: hash }
    })
    res.status(200).json(cliente)
  } catch (error) {
    res.status(400).json(error)
  }
})
export default router