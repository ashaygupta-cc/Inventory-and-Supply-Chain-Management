import { PrismaClient } from '@prisma/client';
import bcrypt from 'bcryptjs';

process.env.DATABASE_URL = "mongodb://localhost:27017/stockly";

const prisma = new PrismaClient();

async function main() {
  console.log('Adding demo accounts for frontend dropdown...');
  const demoPassword = await bcrypt.hash('12345678', 10);

  const accounts = [
    { email: 'test@admin.com', name: 'Demo Admin', role: 'admin' },
    { email: 'test@supplier.com', name: 'Demo Supplier', role: 'supplier' },
    { email: 'test@client.com', name: 'Demo Client', role: 'client' },
  ];

  for (const acc of accounts) {
    const exists = await prisma.user.findUnique({ where: { email: acc.email } });
    if (!exists) {
      await prisma.user.create({
        data: {
          email: acc.email,
          name: acc.name,
          password: demoPassword,
          role: acc.role,
          createdAt: new Date(),
        }
      });
      console.log(`Created ${acc.email} with role ${acc.role}`);
    } else {
      console.log(`${acc.email} already exists.`);
    }
  }
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
