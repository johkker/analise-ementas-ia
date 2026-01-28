"use client";

import { useState } from "react";
import { 
  AlertTriangle, 
  Database, 
  Sparkles, 
  ExternalLink,
  Linkedin,
  Coffee,
  Briefcase,
  Heart,
  Shield,
  Code,
  Check,
  Copy
} from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import Link from "next/link";

export default function AboutPage() {
  const [copied, setCopied] = useState(false);
  const pixKey = "45493261000107"; // TODO: Update with your actual PIX key
  const linkedinUrl = "https://www.linkedin.com/in/johkker"; // TODO: Update with your actual LinkedIn URL

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(pixKey);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error("Failed to copy:", err);
    }
  };

  return (
    <div className="space-y-12 pb-20 max-w-5xl mx-auto">
      {/* Hero */}
      <div className="text-center space-y-6 pt-16">
        <Badge variant="outline" className="px-4 py-1 border-primary/30 text-primary bg-primary/5 uppercase tracking-widest text-[10px] font-black">
          Sobre o Projeto
        </Badge>
        <h1 className="text-5xl md:text-7xl font-heading font-black tracking-tighter leading-[0.9]">
          Transparência com <span className="bg-clip-text text-transparent bg-gradient-to-r from-primary via-emerald-400 to-emerald-500">Responsabilidade</span>
        </h1>
        <p className="text-xl text-muted-foreground max-w-2xl mx-auto font-medium leading-relaxed">
          Uma plataforma independente para facilitar o acompanhamento da atividade parlamentar brasileira.
        </p>
      </div>

      {/* Data Source Disclaimer */}
      <Card className="glass border-yellow-500/20 bg-yellow-500/5">
        <CardContent className="p-8 space-y-6">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 rounded-2xl bg-yellow-500/20 flex items-center justify-center shrink-0">
              <AlertTriangle className="w-6 h-6 text-yellow-500" />
            </div>
            <div className="space-y-4 flex-1">
              <h2 className="text-2xl font-heading font-black tracking-tight">Aviso Importante sobre os Dados</h2>
              
              <div className="space-y-3 text-muted-foreground leading-relaxed">
                <p className="flex items-start gap-2">
                  <Database className="w-5 h-5 text-primary shrink-0 mt-0.5" />
                  <span><strong className="text-foreground">Fonte de Dados:</strong> Todas as informações sobre gastos, proposições e votações são obtidas diretamente da API oficial de Dados Abertos da Câmara dos Deputados. Este projeto não gera ou modifica dados primários.</span>
                </p>
                
                <p className="flex items-start gap-2">
                  <Sparkles className="w-5 h-5 text-secondary shrink-0 mt-0.5" />
                  <span><strong className="text-foreground">Análises por IA:</strong> As análises e resumos gerados por inteligência artificial são <strong className="text-yellow-500">suposições e interpretações automatizadas</strong>, não constituindo verdades absolutas ou pareceres oficiais. Sempre verifique as informações originais antes de tomar qualquer decisão.</span>
                </p>
                
                <p className="flex items-start gap-2">
                  <Shield className="w-5 h-5 text-blue-500 shrink-0 mt-0.5" />
                  <span><strong className="text-foreground">Propósito:</strong> Este site é um ponto de entrada para facilitar a visualização e compreensão inicial da atividade parlamentar. Não substitui a consulta aos canais oficiais da Câmara dos Deputados.</span>
                </p>
              </div>

              <div className="pt-4 border-t border-yellow-500/20">
                <Link href="https://dadosabertos.camara.leg.br/" target="_blank" rel="noopener noreferrer">
                  <Button variant="outline" size="sm" className="border-yellow-500/30 hover:bg-yellow-500/10 font-bold">
                    Acessar Dados Abertos da Câmara <ExternalLink className="w-4 h-4 ml-2" />
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Developer Section */}
      <div className="grid md:grid-cols-2 gap-8">
        {/* Profile Card */}
        <Card className="glass border-primary/20 bg-primary/[0.02]">
          <CardContent className="p-8 space-y-6">
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 rounded-2xl bg-primary/20 flex items-center justify-center">
                <Code className="w-8 h-8 text-primary" />
              </div>
              <div>
                <h3 className="text-2xl font-heading font-black tracking-tight">Desenvolvedor</h3>
                <p className="text-sm text-muted-foreground font-medium">Criado com dedicação por um desenvolvedor independente</p>
              </div>
            </div>

            <div className="space-y-4">
              <p className="text-muted-foreground leading-relaxed">
                Este projeto foi desenvolvido de forma independente como uma ferramenta de transparência e educação cívica. Todo o código é open-source e mantido voluntariamente.
              </p>

              <div className="flex items-center gap-2 p-4 rounded-xl bg-blue-500/10 border border-blue-500/20">
                <Briefcase className="w-5 h-5 text-blue-500 shrink-0" />
                <p className="text-sm font-medium">
                  <strong className="text-foreground">Buscando oportunidades:</strong> Desenvolvedor Full-Stack disponível para projetos freelance ou contratação.
                </p>
              </div>

              <Link href={linkedinUrl} target="_blank" rel="noopener noreferrer">
                <Button className="w-full bg-blue-600 hover:bg-blue-700 font-bold rounded-xl h-12 gap-2">
                  <Linkedin className="w-5 h-5" />
                  Conectar no LinkedIn
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>

        {/* Support Card */}
        <Card className="glass border-emerald-500/20 bg-emerald-500/[0.02]">
          <CardContent className="p-8 space-y-6">
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 rounded-2xl bg-emerald-500/20 flex items-center justify-center">
                <Heart className="w-8 h-8 text-emerald-500" />
              </div>
              <div>
                <h3 className="text-2xl font-heading font-black tracking-tight">Apoie o Projeto</h3>
                <p className="text-sm text-muted-foreground font-medium">Ajude a manter esta plataforma no ar</p>
              </div>
            </div>

            <div className="space-y-4">
              <p className="text-muted-foreground leading-relaxed">
                Manter servidores, APIs e infraestrutura tem custos. Se este projeto te ajudou, considere fazer uma doação para mantê-lo online e acessível para todos.
              </p>

              <div className="space-y-3">
                <div className="p-4 rounded-xl bg-white/5 border border-white/10">
                  <p className="text-[10px] font-black uppercase tracking-widest text-muted-foreground mb-2">Chave PIX</p>
                  <code className="text-sm font-mono text-primary font-bold break-all">
                    {pixKey}
                  </code>
                </div>

                <Button 
                  variant="outline" 
                  className="w-full border-emerald-500/30 hover:bg-emerald-500/10 font-bold rounded-xl h-12 gap-2"
                  onClick={copyToClipboard}
                >
                  {copied ? (
                    <>
                      <Check className="w-5 h-5" />
                      Copiado!
                    </>
                  ) : (
                    <>
                      <Copy className="w-5 h-5" />
                      Copiar Chave PIX
                    </>
                  )}
                </Button>
              </div>

              <p className="text-xs text-muted-foreground italic text-center pt-2">
                Qualquer valor é muito bem-vindo e ajuda a manter o projeto vivo! 💚
              </p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Tech Stack */}
      <Card className="glass">
        <CardContent className="p-8 space-y-6">
          <h3 className="text-2xl font-heading font-black tracking-tight">Stack Tecnológica</h3>
          
          <div className="grid md:grid-cols-2 gap-6">
            <div className="space-y-3">
              <h4 className="text-sm font-black uppercase tracking-widest text-muted-foreground">Frontend</h4>
              <div className="flex flex-wrap gap-2">
                <Badge variant="outline" className="border-white/10 bg-white/5">Next.js 15</Badge>
                <Badge variant="outline" className="border-white/10 bg-white/5">React Query</Badge>
                <Badge variant="outline" className="border-white/10 bg-white/5">TypeScript</Badge>
                <Badge variant="outline" className="border-white/10 bg-white/5">Tailwind CSS</Badge>
              </div>
            </div>

            <div className="space-y-3">
              <h4 className="text-sm font-black uppercase tracking-widest text-muted-foreground">Backend</h4>
              <div className="flex flex-wrap gap-2">
                <Badge variant="outline" className="border-white/10 bg-white/5">FastAPI</Badge>
                <Badge variant="outline" className="border-white/10 bg-white/5">PostgreSQL</Badge>
                <Badge variant="outline" className="border-white/10 bg-white/5">SQLAlchemy</Badge>
                <Badge variant="outline" className="border-white/10 bg-white/5">Google Gemini AI</Badge>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Coming Soon */}
      <Card className="glass border-primary/20 bg-gradient-to-br from-primary/5 to-transparent">
        <CardContent className="p-8 space-y-6">
          <div className="flex items-center gap-3">
            <Sparkles className="w-8 h-8 text-primary" />
            <h3 className="text-2xl font-heading font-black tracking-tight">Em Breve</h3>
          </div>
          
          <p className="text-muted-foreground leading-relaxed">
            Estamos trabalhando em recursos avançados para tornar o acompanhamento parlamentar ainda mais eficiente:
          </p>

          <div className="grid md:grid-cols-2 gap-4">
            <div className="p-4 rounded-xl bg-white/5 border border-white/10 space-y-2">
              <div className="flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-emerald-400" />
                <h4 className="font-bold text-foreground">Análises de IA Aprofundadas</h4>
              </div>
              <p className="text-sm text-muted-foreground">
                Resumos automáticos de proposições e identificação de padrões suspeitos em gastos.
              </p>
            </div>

            <div className="p-4 rounded-xl bg-white/5 border border-white/10 space-y-2">
              <div className="flex items-center gap-2">
                <AlertTriangle className="w-5 h-5 text-yellow-400" />
                <h4 className="font-bold text-foreground">Sistema de Notificações</h4>
              </div>
              <p className="text-sm text-muted-foreground">
                Alertas em tempo real sobre atividades dos deputados que você acompanha.
              </p>
            </div>

            <div className="p-4 rounded-xl bg-white/5 border border-white/10 space-y-2">
              <div className="flex items-center gap-2">
                <ExternalLink className="w-5 h-5 text-blue-400" />
                <h4 className="font-bold text-foreground">Lembretes por Email</h4>
              </div>
              <p className="text-sm text-muted-foreground">
                Receba resumos semanais das atividades parlamentares diretamente no seu email.
              </p>
            </div>

            <div className="p-4 rounded-xl bg-white/5 border border-white/10 space-y-2">
              <div className="flex items-center gap-2">
                <Briefcase className="w-5 h-5 text-purple-400" />
                <h4 className="font-bold text-foreground">Rastreamento de Deputados</h4>
              </div>
              <p className="text-sm text-muted-foreground">
                Acompanhe deputados específicos e receba relatórios personalizados sobre suas ações.
              </p>
            </div>
          </div>

          <div className="pt-4 border-t border-white/10">
            <p className="text-sm text-muted-foreground italic text-center">
              Quer ser notificado quando esses recursos forem lançados? Conecte-se no LinkedIn! 🚀
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
