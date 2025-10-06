import { PrismaClient } from "@prisma/client"
import { Router } from "express"
const prisma = new PrismaClient()
const router = Router()


router.post("/", async (req, res) => {
  const { nome } = req.body;


   try {
    const vendedora = await prisma.vendedora.create({data: {nome: nome},});
    

    res.status(200).json(vendedora)
}  catch (error) {
    console.error(error);
    res.status(400).json({ erro: "Erro ao salvar vendedora", detalhe: error });
  }
});

router.get("/", async (req, res) => {
  try {
    const vendedoras = await prisma.vendedora.findMany({
      select: { nome: true },
      orderBy: { nome: "asc" },
    });

    res.status(200).json(vendedoras.map((v) => v.nome));
  } catch (error) {
    console.error(error);
    res.status(500).json({ erro: "Erro ao buscar nomes", detalhe: error });
  }
});

router.delete("/:nome", async (req, res) => {
  const { nome } = req.params;

  try {
    await prisma.vendedora.delete({
      where: { nome },
    });

    res.status(200).json({ mensagem: "Nome removido com sucesso" });
  } catch (error) {
    console.error(error);
    res.status(400).json({ erro: "Erro ao remover nome", detalhe: error });
  }
});

export default router;