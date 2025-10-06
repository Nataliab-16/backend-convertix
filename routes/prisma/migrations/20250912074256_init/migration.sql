-- CreateTable
CREATE TABLE "clientes" (
    "id" VARCHAR(100) NOT NULL,
    "nome" VARCHAR(60) NOT NULL,
    "email" VARCHAR(60) NOT NULL,
    "senha" VARCHAR(60) NOT NULL,

    CONSTRAINT "clientes_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "vendas" (
    "id" VARCHAR(100) NOT NULL,
    "total" DOUBLE PRECISION NOT NULL,
    "idVendedora" BIGINT NOT NULL,
    "nomeVendedora" VARCHAR(255) NOT NULL,
    "dataHora" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "vendas_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "clientes_email_key" ON "clientes"("email");
