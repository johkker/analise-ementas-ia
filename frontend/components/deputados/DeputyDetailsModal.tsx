"use client";

import { useQuery } from "@tanstack/react-query";
import { 
  X, 
  Receipt, 
  FileText, 
  BarChart3, 
  Mail, 
  MapPin, 
  ChevronRight,
  ExternalLink,
  Sparkles,
  Calendar,
  Building2
} from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { fetchAPI } from "@/lib/api";
import Image from "next/image";
import { useState } from "react";
import { cn } from "@/lib/utils";
import { useRouter } from "next/navigation";

interface DeputyDetailsModalProps {
  deputadoId: number | null;
  isOpen: boolean;
  onClose: () => void;
}

export function DeputyDetailsModal({ deputadoId, isOpen, onClose }: DeputyDetailsModalProps) {
  const [activeTab, setActiveTab] = useState<"gastos" | "proposicoes" | "votos">("gastos");
  const router = useRouter();

  // 1. Basic Info
  const { data: deputado, isLoading: loadingInfo } = useQuery({
    queryKey: ['deputado', deputadoId],
    queryFn: () => deputadoId ? fetchAPI(`/deputados/${deputadoId}`) : null,
    enabled: !!deputadoId && isOpen,
  });

  // 2. Recent Gastos
  const { data: gastosData, isLoading: loadingGastos } = useQuery({
    queryKey: ['deputado-gastos', deputadoId],
    queryFn: () => deputadoId ? fetchAPI(`/gastos/exploration?politico_id=${deputadoId}&page_size=5`) : null,
    enabled: !!deputadoId && isOpen && activeTab === "gastos",
  });

  // 3. Propositions
  const { data: proposicoes, isLoading: loadingProps } = useQuery({
    queryKey: ['deputado-props', deputadoId],
    queryFn: () => deputadoId ? fetchAPI(`/proposicoes/?politico_id=${deputadoId}&limit=10`) : null,
    enabled: !!deputadoId && isOpen && activeTab === "proposicoes",
  });

  if (!deputadoId) return null;

  const tabs = [
    { id: "gastos", label: "Gastos Recentes", icon: Receipt },
    { id: "proposicoes", label: "Proposições", icon: FileText },
    { id: "votos", label: "Frequência", icon: BarChart3 },
  ];

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="glass border-white/10 p-0 overflow-hidden rounded-3xl sm:max-w-2xl md:max-w-3xl">
        <DialogHeader className="sr-only">
          <DialogTitle>Detalhes do Deputado: {deputado?.nome_parlamentar}</DialogTitle>
          <DialogDescription>
            Informações detalhadas sobre gastos, proposições e atuação parlamentar de {deputado?.nome_parlamentar}.
          </DialogDescription>
        </DialogHeader>

        <div className="relative">
          {/* Header/Cover */}
          <div className="h-40 bg-gradient-to-r from-primary/20 via-primary/5 to-transparent relative overflow-hidden">
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_50%,#00A85915,transparent_50%)]" />
          </div>

          <div className="px-8 pb-8 -mt-16 relative z-10">
            <div className="flex flex-col md:flex-row gap-8 items-start">
              {/* Profile Image */}
              <div className="relative w-28 h-28 sm:w-40 sm:h-40 rounded-3xl overflow-hidden border-4 border-slate-900 shadow-2xl shrink-0 bg-muted">
                {deputado?.foto_url && (
                  <Image src={deputado.foto_url} alt={deputado.nome_parlamentar} fill sizes="160px" className="object-cover" />
                )}
              </div>

              {/* Bio Info */}
              <div className="flex-1 space-y-4 pt-16 md:pt-20">
                <div className="flex flex-wrap items-center gap-3">
                  <h2 className="text-3xl font-heading font-black tracking-tighter">{deputado?.nome_parlamentar}</h2>
                  <Badge className="bg-primary/20 text-primary border-primary/30 uppercase font-black text-[10px] px-3">
                    {deputado?.partido?.sigla}
                  </Badge>
                  <Badge variant="outline" className="border-white/10 text-muted-foreground uppercase font-bold text-[10px]">
                    {deputado?.uf}
                  </Badge>
                </div>

                <div className="flex flex-wrap gap-6 text-sm text-muted-foreground font-medium">
                  <div className="flex items-center gap-2">
                    <Mail className="w-4 h-4 text-primary" /> {deputado?.email || "E-mail não disponível"}
                  </div>
                  <div className="flex items-center gap-2">
                    <MapPin className="w-4 h-4 text-primary" /> Gabinete Digital
                  </div>
                </div>
              </div>
            </div>

            {/* Tabs Navigation */}
            <div className="mt-12 flex gap-2 border-b border-white/5 pb-px">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={cn(
                    "flex items-center gap-2 px-6 py-4 text-sm font-bold transition-all relative",
                    activeTab === tab.id 
                      ? "text-primary" 
                      : "text-muted-foreground hover:text-foreground"
                  )}
                >
                  <tab.icon className="w-4 h-4" />
                  {tab.label}
                  {activeTab === tab.id && (
                    <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary shadow-[0_0_10px_#00A859]" />
                  )}
                </button>
              ))}
            </div>

            {/* Tab Content with Scroll Fallback */}
            <div className="mt-8 max-h-[400px] min-h-[300px] overflow-y-auto pr-2 scrollbar-thin scrollbar-thumb-primary/20 hover:scrollbar-thumb-primary/40 scrollbar-track-transparent">
              {activeTab === "gastos" && (
                <div className="space-y-4">
                  {loadingGastos ? (
                    [...Array(3)].map((_, i) => <div key={i} className="h-20 glass rounded-2xl animate-pulse" />)
                  ) : (
                    gastosData?.items.map((g: any) => (
                      <div key={g.id} className="glass-light hover:bg-white/5 p-4 rounded-2xl flex items-center justify-between group transition-all">
                        <div className="flex items-center gap-4">
                          <div className="w-10 h-10 rounded-xl bg-white/5 flex items-center justify-center">
                            <Receipt className="w-5 h-5 text-muted-foreground" />
                          </div>
                          <div>
                            <p className="font-bold text-sm">{g.tipo}</p>
                            <p className="text-[10px] uppercase font-black text-muted-foreground flex items-center gap-1">
                              <Building2 className="w-3 h-3" /> {g.fornecedor}
                            </p>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="font-black text-foreground">R$ {g.valor.toLocaleString('pt-BR')}</p>
                          <p className="text-[10px] font-bold text-muted-foreground flex items-center gap-1 justify-end">
                            <Calendar className="w-3 h-3" /> {new Date(g.data).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                    ))
                  )}
                  <Button variant="link" className="text-primary font-bold text-sm" onClick={() => {
                    onClose();
                    router.push(`/gastos?nome=${deputado?.nome_parlamentar}`);
                  }}>
                    Ver auditoria completa <ExternalLink className="w-3 h-3 ml-2" />
                  </Button>
                </div>
              )}

              {activeTab === "proposicoes" && (
                <div className="space-y-4">
                   {loadingProps ? (
                     [...Array(3)].map((_, i) => <div key={i} className="h-24 glass rounded-2xl animate-pulse" />)
                   ) : (
                     proposicoes?.map((p: any) => (
                       <div key={p.id} className="glass-light p-5 rounded-2xl space-y-3">
                          <div className="flex justify-between items-start">
                             <h4 className="font-black font-heading text-primary">{p.sigla_tipo} {p.numero}/{p.ano}</h4>
                             {p.analise && <Sparkles className="w-4 h-4 text-emerald-400" />}
                          </div>
                          <p className="text-sm text-muted-foreground leading-relaxed line-clamp-2 italic">
                            "{p.ementa}"
                          </p>
                          <Button variant="ghost" size="sm" className="h-8 text-[10px] font-black uppercase text-muted-foreground p-0" disabled>
                             Análise Técnica por IA em breve <ChevronRight className="w-3 h-3 ml-1" />
                          </Button>
                       </div>
                     ))
                   )}
                </div>
              )}

              {activeTab === "votos" && (
                <div className="flex flex-col items-center justify-center py-12 text-center space-y-4">
                  <BarChart3 className="w-16 h-16 text-muted/20" />
                  <p className="text-muted-foreground font-medium max-w-sm">
                    Módulo de Votações e Frequência será liberado na próxima atualização do sistema.
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
