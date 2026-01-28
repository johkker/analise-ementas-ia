"use client";

import { FileText, Sparkles, Clock, ArrowRight } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import Link from "next/link";

export default function ProposicoesPage() {
  return (
    <div className="min-h-[70vh] flex items-center justify-center pb-20 pt-8">
      <Card className="glass border-primary/20 max-w-2xl mx-auto">
        <CardContent className="p-16 text-center space-y-8">
          {/* Icon */}
          <div className="flex justify-center">
            <div className="w-24 h-24 rounded-3xl bg-primary/10 flex items-center justify-center relative">
              <FileText className="w-12 h-12 text-primary" />
              <div className="absolute -top-2 -right-2 w-8 h-8 rounded-full bg-yellow-500/20 flex items-center justify-center">
                <Clock className="w-4 h-4 text-yellow-500" />
              </div>
            </div>
          </div>

          {/* Content */}
          <div className="space-y-4">
            <Badge variant="outline" className="px-4 py-1 border-primary/30 text-primary bg-primary/5 uppercase tracking-widest text-[10px] font-black">
              Em Desenvolvimento
            </Badge>
            
            <h1 className="text-4xl md:text-5xl font-heading font-black tracking-tighter">
              Explorador de Proposições
            </h1>
            
            <p className="text-lg text-muted-foreground max-w-lg mx-auto leading-relaxed">
              Estamos construindo uma interface completa para explorar, filtrar e analisar todas as proposições legislativas da Câmara dos Deputados.
            </p>
          </div>

          {/* Features Preview */}
          <div className="grid md:grid-cols-2 gap-4 pt-4">
            <div className="p-4 rounded-xl bg-white/5 border border-white/10 text-left space-y-2">
              <div className="flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-emerald-400" />
                <h3 className="font-bold text-sm">Análise por IA</h3>
              </div>
              <p className="text-xs text-muted-foreground">
                Resumos automáticos e classificação de proposições por tema e impacto.
              </p>
            </div>

            <div className="p-4 rounded-xl bg-white/5 border border-white/10 text-left space-y-2">
              <div className="flex items-center gap-2">
                <FileText className="w-5 h-5 text-blue-400" />
                <h3 className="font-bold text-sm">Filtros Avançados</h3>
              </div>
              <p className="text-xs text-muted-foreground">
                Busque por autor, tema, período, status de tramitação e muito mais.
              </p>
            </div>
          </div>

          {/* CTA */}
          <div className="pt-6 space-y-4">
            <p className="text-sm text-muted-foreground">
              Enquanto isso, você pode explorar os deputados e seus gastos:
            </p>
            <div className="flex flex-col sm:flex-row gap-3 justify-center">
              <Link href="/deputados">
                <Button className="bg-primary hover:bg-emerald-500 font-bold rounded-xl gap-2">
                  Ver Deputados <ArrowRight className="w-4 h-4" />
                </Button>
              </Link>
              <Link href="/gastos">
                <Button variant="outline" className="border-white/10 hover:bg-white/5 font-bold rounded-xl gap-2">
                  Auditoria de Gastos <ArrowRight className="w-4 h-4" />
                </Button>
              </Link>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
