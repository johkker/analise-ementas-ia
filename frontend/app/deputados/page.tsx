"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { 
  Users, 
  Search, 
  MapPin, 
  ChevronRight,
  Filter,
  User
} from "lucide-react";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { fetchAPI } from "@/lib/api";
import Image from "next/image";
import { DeputyDetailsModal } from "@/components/deputados/DeputyDetailsModal";

export default function DeputadosPage() {
  const [search, setSearch] = useState("");
  const [partido, setPartido] = useState("all");
  const [uf, setUf] = useState("all");
  
  // Modal State
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const openModal = (id: number) => {
    setSelectedId(id);
    setIsModalOpen(true);
  };

  const { data: deputados, isLoading } = useQuery({
    queryKey: ['deputados', { partido, uf }],
    queryFn: async () => {
      let url = "/deputados/?";
      if (partido !== "all") url += `&partido=${partido}`;
      if (uf !== "all") url += `&uf=${uf}`;
      return fetchAPI(url);
    }
  });

  const filteredDeputados = deputados?.filter((d: any) => 
    d.nome_parlamentar.toLowerCase().includes(search.toLowerCase())
  ) || [];

  return (
    <div className="space-y-8 pb-20">
      <div className="flex flex-col space-y-4 text-center items-center">
        <h1 className="text-4xl md:text-5xl font-heading font-black tracking-tighter flex items-center gap-3">
          <Users className="w-12 h-12 text-primary" /> Representantes do Povo
        </h1>
        <p className="text-muted-foreground font-medium max-w-2xl">
          Pesquise e acompanhe o desempenho dos 513 deputados federais. Veja gastos, votações e proposições de cada parlamentar em um só lugar.
        </p>
      </div>

      {/* Search & Filters */}
      <Card className="glass border-white/5 p-4 rounded-3xl max-w-4xl mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="relative col-span-1 md:col-span-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input 
              placeholder="Buscar por nome..." 
              className="pl-10 glass-hover border-white/10 rounded-xl h-12"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>

          <select 
            value={partido} 
            onChange={(e) => setPartido(e.target.value)}
            className="flex h-12 w-full rounded-xl border border-white/10 bg-white/5 backdrop-blur-md px-3 py-2 text-sm appearance-none glass-hover cursor-pointer outline-none focus:ring-2 focus:ring-primary/50"
          >
            <option value="all" className="bg-slate-900">Todos os Partidos</option>
            <option value="PT" className="bg-slate-900">PT</option>
            <option value="PL" className="bg-slate-900">PL</option>
            <option value="PP" className="bg-slate-900">PP</option>
            <option value="UNIÃO" className="bg-slate-900">UNIÃO</option>
            <option value="MDB" className="bg-slate-900">MDB</option>
            <option value="PSD" className="bg-slate-900">PSD</option>
          </select>

          <select 
            value={uf} 
            onChange={(e) => setUf(e.target.value)}
            className="flex h-12 w-full rounded-xl border border-white/10 bg-white/5 backdrop-blur-md px-3 py-2 text-sm appearance-none glass-hover cursor-pointer outline-none focus:ring-2 focus:ring-primary/50"
          >
            <option value="all" className="bg-slate-900">Todos os Estados</option>
            {["AC","AL","AP","AM","BA","CE","DF","ES","GO","MA","MT","MS","MG","PA","PB","PR","PE","PI","RJ","RN","RS","RO","RR","SC","SP","SE","TO"].map(sigla => (
              <option key={sigla} value={sigla} className="bg-slate-900">{sigla}</option>
            ))}
          </select>
        </div>
      </Card>

      {/* Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {[...Array(8)].map((_, i) => (
            <div key={i} className="h-72 glass rounded-3xl animate-pulse" />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {filteredDeputados.map((dep: any) => (
            <Card 
              key={dep.id} 
              className="glass-hover border-white/5 group cursor-pointer overflow-hidden transition-all duration-300"
              onClick={() => openModal(dep.id)}
            >
              <CardContent className="p-0">
                <div className="relative h-48 w-full bg-muted/20">
                  {dep.foto_url ? (
                    <Image 
                      src={dep.foto_url} 
                      alt={dep.nome_parlamentar}
                      fill
                      className="object-cover transition-transform duration-500 group-hover:scale-110"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center">
                       <User className="w-12 h-12 text-muted/30" />
                    </div>
                  )}
                  <div className="absolute inset-0 bg-gradient-to-t from-slate-950/80 to-transparent" />
                  <div className="absolute bottom-4 left-4 right-4">
                     <Badge className="bg-primary/20 backdrop-blur-md border-primary/30 text-primary mb-1">
                        {dep.partido?.sigla}
                     </Badge>
                     <h3 className="text-white font-bold text-lg leading-tight truncate">{dep.nome_parlamentar}</h3>
                  </div>
                </div>
                <div className="p-4 flex items-center justify-between">
                   <div className="flex items-center gap-1.5 text-xs text-muted-foreground font-bold">
                      <MapPin className="w-3.5 h-3.5" /> {dep.uf}
                   </div>
                   <Button variant="ghost" size="sm" className="rounded-full gap-1 text-xs font-black uppercase text-primary">
                      Ver Perfil <ChevronRight className="w-3.5 h-3.5" />
                   </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {filteredDeputados.length === 0 && !isLoading && (
        <div className="py-20 text-center flex flex-col items-center justify-center space-y-4">
           <Users className="w-16 h-16 text-muted/30" />
           <p className="text-muted-foreground font-medium">Nenhum deputado encontrado com esses critérios.</p>
        </div>
      )}

      <DeputyDetailsModal 
        deputadoId={selectedId}
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
      />
    </div>
  );
}
