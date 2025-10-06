/*
  Warnings:

  - A unique constraint covering the columns `[nome]` on the table `vendedoras` will be added. If there are existing duplicate values, this will fail.

*/
-- CreateIndex
CREATE UNIQUE INDEX "vendedoras_nome_key" ON "vendedoras"("nome");
