"use client";

import { 
  ArrowUpRight, 
  TrendingUp, 
  AlertTriangle, 
  ShieldCheck, 
  User, 
  PieChart, 
  Receipt, 
  Zap 
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { fetchAPI, endpoints } from "@/lib/api";
import Link from "next/link";
import Image from "next/image";
import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { DeputyDetailsModal } from "@/components/deputados/DeputyDetailsModal";

export default function Home() {
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const openModal = (id: number) => {
    setSelectedId(id);
    setIsModalOpen(true);
  };

  const { data: stats, isLoading: loadingStats } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: () => fetchAPI(endpoints.stats),
    staleTime: 1000 * 60 * 5, // 5 minutes
  });

  const { data: featuredProposicao, isLoading: loadingFeatured } = useQuery({
    queryKey: ['featured-proposicao'],
    queryFn: async () => {
      const data = await fetchAPI(`${endpoints.proposicoes}?limit=1`);
      return data.items?.[0] || data[0] || null;
    },
    staleTime: 1000 * 60 * 10, // 10 minutes
  });

  return (
    <main className="space-y-12 pb-20">
      {/* Hero Section */}
      <section className="text-center space-y-6 pt-16 relative">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-full bg-primary/5 blur-[120px] -z-10 rounded-full" />
        <Badge variant="outline" className="px-4 py-1 border-primary/30 text-primary bg-primary/5 animate-pulse uppercase tracking-widest text-[10px] font-black">
          Monitor de Transparência 2026
        </Badge>
        <h1 className="text-6xl md:text-8xl font-heading font-black tracking-tighter leading-[0.9] max-w-5xl mx-auto">
          O Poder sob <span className="bg-clip-text text-transparent bg-gradient-to-r from-primary via-emerald-400 to-emerald-500">Lente Digital.</span>
        </h1>
        <p className="text-xl text-muted-foreground max-w-2xl mx-auto font-medium leading-relaxed">
          Analisamos gastos parlamentares, votações e proposições da Câmara com IA para entregar transparência pura e sem ruídos.
        </p>
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-8">
          <Link href="/deputados">
            <Button size="lg" className="rounded-2xl px-10 h-16 text-lg font-bold shadow-2xl shadow-emerald-500/20 bg-primary hover:bg-emerald-500 transition-all">
              Explorar Deputados
            </Button>
          </Link>
          <Link href="/gastos">
            <Button size="lg" variant="outline" className="rounded-2xl px-10 h-16 text-lg font-bold glass-hover border-white/10">
              Auditoria de Gastos
            </Button>
          </Link>
        </div>
      </section>

      {/* Main Stats Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="glass group relative overflow-hidden">
          <div className="absolute top-0 right-0 w-24 h-24 bg-primary/10 blur-3xl rounded-full -mr-12 -mt-12" />
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">Gastos Totais (2026)</CardTitle>
            <TrendingUp className="h-4 w-4 text-primary" />
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-black font-heading tabular-nums">
              {stats ? `R$ ${(stats.total_gastos / 1000000).toFixed(1)}M` : "---"}
            </div>
            <p className="text-[10px] text-muted-foreground mt-2 flex items-center gap-1 font-bold">
              <Zap className="w-3 h-3 text-secondary" /> {stats?.year || 2026} Fiscal Year
            </p>
          </CardContent>
        </Card>

        <Card className="glass group">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">Projetos Monitorados</CardTitle>
            <AlertTriangle className="h-4 w-4 text-secondary" />
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-black font-heading tabular-nums text-foreground">
              {stats?.total_proposicoes || "---"}
            </div>
            <p className="text-[10px] text-muted-foreground mt-2 font-bold">
              Análise de impacto em tempo real
            </p>
          </CardContent>
        </Card>

        <Card className="glass group">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">Deputados Ativos</CardTitle>
            <ShieldCheck className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-black font-heading tabular-nums text-foreground">
              {stats?.total_deputados || "---"}
            </div>
            <p className="text-[10px] text-muted-foreground mt-2 font-bold">
              Representantes monitorados
            </p>
          </CardContent>
        </Card>

        <Card className="glass group border-primary/20 bg-primary/[0.02]">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-[10px] font-black uppercase tracking-widest text-primary">Oportunidade de Economia</CardTitle>
            <ArrowUpRight className="h-4 w-4 text-primary animate-bounce-slow" />
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-black font-heading tabular-nums text-primary">
              {stats ? `R$ ${(stats.savings_opportunity_estimate / 1000).toFixed(0)}k` : "---"}
            </div>
            <p className="text-[10px] text-muted-foreground mt-2 font-bold">
              Estimativa de corte em anomalias
            </p>
          </CardContent>
        </Card>
      </div>

      <div className="grid lg:grid-cols-3 gap-8">
        {/* Left: Top Spenders */}
        <div className="lg:col-span-2 space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-heading font-black tracking-tight flex items-center gap-2">
              <User className="text-primary w-6 h-6" /> Maiores Gastos do Mês
            </h2>
            <Link href="/gastos">
              <Button variant="link" size="sm" className="text-[10px] font-black uppercase tracking-widest text-primary p-0">
                Ver Ranking Completo
              </Button>
            </Link>
          </div>
          <div className="grid sm:grid-cols-2 gap-4">
            {stats?.top_spenders?.map((politico: any, idx: number) => (
              <Card 
                key={idx} 
                className="glass-light border-white/5 hover:border-primary/30 transition-all cursor-pointer group overflow-hidden"
                onClick={() => politico.id && openModal(politico.id)}
              >
                <CardContent className="p-4 flex items-center gap-4">
                  <div className="relative w-16 h-16 rounded-xl overflow-hidden bg-muted border border-white/10 shrink-0">
                    {politico.foto_url && (
                      <Image 
                        src={politico.foto_url} 
                        alt={politico.nome} 
                        fill 
                        className="object-cover grayscale group-hover:grayscale-0 transition-all duration-500"
                      />
                    )}
                  </div>
                  <div className="flex flex-col min-w-0">
                    <span className="text-sm font-bold truncate pr-4">{politico.nome}</span>
                    <span className="text-xl font-black font-heading text-primary">R$ {politico.valor.toLocaleString('pt-BR')}</span>
                    <span className="text-[9px] uppercase tracking-tighter text-muted-foreground font-black">Cota Parlamentar Total</span>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Right: Categories */}
        <div className="space-y-6">
          <h2 className="text-2xl font-heading font-black tracking-tight flex items-center gap-2">
            <PieChart className="text-secondary w-6 h-6" /> Por Categoria
          </h2>
          <Card className="glass h-fit">
            <CardContent className="pt-6 space-y-5">
              {stats?.categories?.map((cat: any, idx: number) => (
                <div key={idx} className="space-y-1">
                  <div className="flex justify-between items-end">
                    <span className="text-[10px] font-bold uppercase tracking-wide truncate max-w-[200px] text-muted-foreground">
                      {cat.categoria}
                    </span>
                    <span className="text-xs font-black tabular-nums">
                      R$ {(cat.valor / 1000).toFixed(0)}k
                    </span>
                  </div>
                  <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-primary" 
                      style={{ 
                        width: `${Math.min(100, (cat.valor / (stats.total_gastos / 5)) * 100)}%` 
                      }} 
                    />
                  </div>
                </div>
              ))}
              <div className="pt-2">
                <Button variant="ghost" className="w-full text-[10px] font-black uppercase tracking-widest text-muted-foreground hover:text-primary h-10">
                  Ver todas as categorias
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Featured Insight Section */}
      <div className="grid lg:grid-cols-2 gap-8 items-center pt-8">
        <div className="space-y-6">
          <h2 className="text-4xl font-heading font-black tracking-tighter leading-none">
            Visão Sistêmica
          </h2>
          {featuredProposicao ? (
            <Card className="glass border-emerald-500/20 relative overflow-hidden group shadow-2xl shadow-primary/5">
              <div className="absolute top-0 right-0 p-4">
                 <Badge className="bg-primary text-primary-foreground font-black text-[10px] uppercase tracking-widest">IA ANALYTICS</Badge>
              </div>
              <CardHeader>
                <CardTitle className="text-2xl font-black pr-20 leading-tight">
                  {featuredProposicao.sigla_tipo} {featuredProposicao.numero}/{featuredProposicao.ano}
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <p className="text-muted-foreground leading-relaxed font-medium line-clamp-4 text-base italic">
                  "{featuredProposicao.ementa}"
                </p>
                <div className="flex items-center justify-between pt-6 border-t border-white/5">
                  <div className="flex items-center gap-6">
                    <div className="flex flex-col">
                        <span className="text-[10px] font-black text-muted-foreground uppercase tracking-widest">Monitoramento</span>
                        <span className="text-xs font-bold text-primary flex items-center gap-1">
                            <ShieldCheck className="w-3 h-3" /> Proteção Social
                        </span>
                    </div>
                  </div>
                  <Link href={`/proposicoes/${featuredProposicao.id}`}>
                    <Button variant="secondary" size="sm" className="rounded-xl font-black text-[10px] uppercase tracking-widest h-10 px-6">
                      Relatório Completo
                    </Button>
                  </Link>
                </div>
              </CardContent>
            </Card>
          ) : (
            <div className="h-64 glass rounded-3xl flex items-center justify-center text-muted-foreground animate-pulse border-white/5">
              Sincronizando análises parlamentares...
            </div>
          )}
        </div>

        <div className="relative aspect-[4/3] glass rounded-[2.5rem] flex flex-col items-center justify-center overflow-hidden border-white/5 p-8 text-center group">
           <div className="absolute inset-0 bg-gradient-to-br from-primary/20 via-transparent to-emerald-500/10 opacity-50 active:opacity-100 transition-opacity" />
           <div className="relative z-10 space-y-4">
              <div className="w-16 h-16 rounded-2xl bg-primary/20 flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform">
                  <Receipt className="w-8 h-8 text-primary" />
              </div>
              <h3 className="text-2xl font-black font-heading tracking-tight">Auditoria Visual</h3>
              <p className="text-muted-foreground font-medium text-sm max-w-[200px] mx-auto">
                 Estamos preparando um mapa de calor para identificar clusters de gastos por região.
              </p>
              <Badge variant="outline" className="border-primary/30 text-primary bg-primary/5">EM BREVE</Badge>
           </div>
        </div>
      </div>

      <DeputyDetailsModal 
        deputadoId={selectedId}
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
      />
    </main>
  );
}
