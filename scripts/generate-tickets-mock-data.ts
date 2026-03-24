import { PrismaClient } from '@prisma/client';

process.env.DATABASE_URL = "mongodb://localhost:27017/stockly";

const prisma = new PrismaClient();

function randomElement<T>(arr: T[]): T {
  return arr[Math.floor(Math.random() * arr.length)];
}

async function main() {
  console.log('Generating Support Tickets, Reviews, and Notifications...');

  const admin = await prisma.user.findUnique({ where: { email: 'test@admin.com' } });
  const client = await prisma.user.findUnique({ where: { email: 'test@client.com' } });

  if (!admin || !client) throw new Error("Missing required test accounts. Please run the add-demo-users script first.");

  const allProducts = await prisma.product.findMany({ take: 20 });
  const allOrders = await prisma.order.findMany({ take: 10 });

  if (allProducts.length === 0) {
    console.log("No products found to attach tickets to.");
    return;
  }

  const subjects = [
    "Where is my order?",
    "Product arrived damaged",
    "How to process a return?",
    "Bulk discount inquiry",
    "Restock timeline for laptops",
    "Login issues on client portal",
    "Missing invoice",
    "Wrong item shipped",
    "Can you expedite shipping?",
    "Payment failed but charged"
  ];
  const statuses = ['open', 'in_progress', 'resolved', 'closed'];
  const priorities = ['low', 'medium', 'high', 'urgent'];

  // Support Tickets
  for (let i = 1; i <= 15; i++) {
    const isClient = Math.random() > 0.5;
    const author = isClient ? client : admin;
    
    const prod = randomElement(allProducts);
    const ord = randomElement(allOrders);

    const ticket = await prisma.supportTicket.create({
      data: {
        subject: randomElement(subjects) + ` - Ticket #${i}`,
        description: "This is a detailed mock description of the issue. I am experiencing problems with this specific order and need assistance as soon as possible. Thank you.",
        status: randomElement(statuses),
        priority: randomElement(priorities),
        userId: author.id,
        productId: Math.random() > 0.5 ? prod.id : null,
        orderId: Math.random() > 0.5 ? ord.id : null,
        assignedToId: Math.random() > 0.3 ? admin.id : null,
        createdAt: new Date(Date.now() - Math.random() * 1000 * 60 * 60 * 24 * 14) // Past 14 days
      }
    });

    const numReplies = Math.floor(Math.random() * 4);
    for (let r = 0; r < numReplies; r++) {
      await prisma.supportTicketReply.create({
        data: {
          ticketId: ticket.id,
          userId: r % 2 === 0 ? admin.id : author.id,
          body: r % 2 === 0 ? "We have received your ticket and are looking into this right now. Please allow 24-48 hours for a complete resolution." : "Thank you for the prompt update. I look forward to hearing a resolution.",
          createdAt: new Date(ticket.createdAt.getTime() + 1000 * 60 * 60 * (r + 1))
        }
      });
    }
  }
  console.log("Created 15 Support Tickets with interactive Replies");

  // Product Reviews
  for (let i = 0; i < 20; i++) {
    const prod = randomElement(allProducts);
    await prisma.productReview.create({
      data: {
        productId: prod.id,
        userId: client.id,
        productName: prod.name,
        rating: Math.floor(Math.random() * 3) + 3, // 3 to 5 stars
        comment: ["Great product!", "Highly recommend this to anyone.", "Decent quality for the price.", "Will buy again for sure.", "Customer support was very helpful along with the product shipping."][Math.floor(Math.random()*5)],
        status: 'approved',
        createdAt: new Date(Date.now() - Math.random() * 1000 * 60 * 60 * 24 * 30) // Past 30 days
      }
    });
  }
  console.log("Created 20 Product Reviews");

  // Notifications
  const notifTypes = ["low_stock", "order_confirmation", "system_alert", "shipping_update"];
  for (let i = 0; i < 12; i++) {
    await prisma.notification.create({
      data: {
        userId: admin.id,
        type: randomElement(notifTypes),
        title: "System Alert " + (i + 1),
        message: "You have a new update regarding your recent activity in the system.",
        read: Math.random() > 0.4,
        createdAt: new Date(Date.now() - Math.random() * 1000 * 60 * 60 * 24 * 7)
      }
    });
  }
  console.log("Created 12 Notifications");

  console.log("Secondary panels (Support Tickets, Reviews, Notifications) generated successfully!");
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
