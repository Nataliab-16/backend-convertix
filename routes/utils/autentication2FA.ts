import { Resend } from 'resend';
const resend = new Resend(process.env.RESEND_API);

export function gerarCodigo(): string {
  return Math.floor(100000 + Math.random() * 900000).toString(); // 6 dígitos
}

const codigosPendentes = new Map<string, { codigo: string; expira: number }>();

export function salvarCodigo(email: string, codigo: string) {
  codigosPendentes.set(email, {
    codigo,
    expira: Date.now() + 5 * 60 * 1000, // 5 minutos
  });
}

export function validarCodigo(email: string, codigoDigitado: string) {
  const registro = codigosPendentes.get(email);
  if (!registro) return false;
  const expirado = Date.now() > registro.expira;
  return !expirado && registro.codigo === codigoDigitado;
}


export async function enviarCodigoPorEmail(email: string, codigo: string) {
  await resend.emails.send({
    from: 'onboarding@resend.dev',
    to: email,
    subject: 'Seu código de verificação',
    html: `<p>Olá! Seu código é: <strong>${codigo}</strong></p>`,
  });
}


