
import { Router } from "express"
import {
  gerarCodigo,
  salvarCodigo,
  validarCodigo,
  enviarCodigoPorEmail,
} from "./utils/autentication2FA";

const router = Router()


// Rota para enviar código por e-mail
router.post("/verificar-email", async (req, res) => {
  const { email } = req.body;

  if (!email || typeof email !== "string") {
    return res.status(400).json({ erro: "Email inválido." });
  }

  try {
    const codigo = gerarCodigo();
    salvarCodigo(email, codigo);
    await enviarCodigoPorEmail(email, codigo);
    res.status(200).json({ mensagem: "Código enviado com sucesso." });
  } catch (error) {
    console.error(error);
    res.status(500).json({ erro: "Erro ao enviar código." });
  }
});

// Rota para validar código
router.post("/verificar-codigo", (req, res) => {
  const { email, codigo } = req.body;

  if (!email || !codigo) {
    return res.status(400).json({ erro: "Email e código são obrigatórios." });
  }

  const valido = validarCodigo(email, codigo);
  if (!valido) {
    return res.status(400).json({ erro: "Código inválido ou expirado." });
  }

  res.status(200).json({ mensagem: "Código verificado com sucesso." });
});

export default router