import React, { Suspense } from "react";
import { Metadata } from "next";
import GastosClient from "@/components/gastos/GastosClient";

export const metadata: Metadata = {
  title: "Gastos - Lente Cidadã",
};

export default function Page() {
  return (
    <div className="container pt-12">
      <Suspense>
        <GastosClient />
      </Suspense>
    </div>
  );
}
