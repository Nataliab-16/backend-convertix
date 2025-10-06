import { PrismaClient } from "@prisma/client"
import { Router } from "express"
import axios from "axios";
const prisma = new PrismaClient()
const router = Router()


router.post("/", async (req, res) => {
  const { eventId, date, version, event, companyId, data } = req.body;

  if (!data) {
    return res.status(400).json({ erro: "Payload inválido." });
  }

   try {
    // Consulta direta à API do Bling
    const resp = await axios.get(`https://convertix-o57c.onrender.com/vendedora/${data.vendedor.id}`);
    console.log(resp.data);
    const {id_vendedora, nome_vendedora} = resp.data
    const nomeVendedora2 = resp.data?.data?.contato?.nome || "";

    const venda = await prisma.venda.create({
      data: {
        id: String(data.id),
        total: data.total,
        idVendedora: (data.vendedor.id),
        nomeVendedora: nome_vendedora,
        dataHora: new Date(date),
      },
    });
    

    return res.json({
  ...venda,
  total: venda.total.toString(),
  idVendedora: venda.idVendedora.toString(),
});
  }  catch (error) {
    console.error(error);
    res.status(400).json({ erro: "Erro ao salvar venda", detalhe: error });
  }
});
export default router