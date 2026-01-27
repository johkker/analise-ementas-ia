import { ArrowUpRight, TrendingUp, AlertTriangle, ShieldCheck, DollarSign } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export default function Home() {
  return (
    <main className="space-y-12">
      {/* Hero Section */}
      <section className="text-center space-y-6 pt-12">
        <Badge variant="outline" className="px-4 py-1 border-primary/30 text-primary bg-primary/5 animate-pulse">
          Plataforma de Transparência Cidadã
        </Badge>
        <h1 className="text-6xl md:text-7xl font-heading font-black tracking-tighter leading-tight max-w-4xl mx-auto">
          Acompanhe o Poder com <span className="bg-clip-text text-transparent bg-gradient-to-r from-primary to-emerald-400">Inteligência Real.</span>
        </h1>
        <p className="text-xl text-muted-foreground max-w-2xl mx-auto font-medium">
          Analisamos cada gasto, voto e projeto de lei da Câmara dos Deputados usando IA para identificar riscos, economia e impacto na sua vida.
        </p>
        <div className="flex items-center justify-center gap-4 pt-4">
          <Button size="lg" className="rounded-full px-8 h-14 text-lg font-bold shadow-xl shadow-emerald-500/20">
            Explorar Deputados
          </Button>
          <Button size="lg" variant="outline" className="rounded-full px-8 h-14 text-lg font-bold glass">
            Ver Proposições
          </Button>
        </div>
      </section>

      {/* Highlights Grid */}
      <div className="grid md:grid-cols-3 gap-6">
        <Card className="glass group cursor-pointer hover:border-primary/50 transition-all duration-300">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-bold uppercase tracking-wider text-muted-foreground">Economia Identificada</CardTitle>
            <div className="p-2 rounded-lg bg-emerald-500/10 text-primary">
              <TrendingUp className="h-5 w-5" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-black font-heading tabular-nums">R$ 1.2M</div>
            <p className="text-xs text-muted-foreground mt-1 flex items-center gap-1">
              <span className="text-primary font-bold">+12%</span> em relação ao mês anterior
            </p>
          </CardContent>
        </Card>

        <Card className="glass group cursor-pointer hover:border-red-500/50 transition-all duration-300">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-bold uppercase tracking-wider text-muted-foreground">Alertas de Risco</CardTitle>
            <div className="p-2 rounded-lg bg-red-500/10 text-red-500">
              <AlertTriangle className="h-5 w-5" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-black font-heading tabular-nums">24</div>
            <p className="text-xs text-muted-foreground mt-1">
              Proposições com indícios de irregularidade
            </p>
          </CardContent>
        </Card>

        <Card className="glass group cursor-pointer hover:border-blue-500/50 transition-all duration-300">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-bold uppercase tracking-wider text-muted-foreground">Análises Realizadas</CardTitle>
            <div className="p-2 rounded-lg bg-blue-500/10 text-blue-500">
              <ShieldCheck className="h-5 w-5" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-black font-heading tabular-nums">458</div>
            <p className="text-xs text-muted-foreground mt-1">
              Processadas por Gemini AI este mês
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Featured Insight Section */}
      <div className="grid lg:grid-cols-2 gap-8 items-center pt-8">
        <div className="space-y-6">
          <h2 className="text-4xl font-heading font-black leading-none">
            Análise em Destaque
          </h2>
          <Card className="glass border-emerald-500/20 relative overflow-hidden group">
            <div className="absolute top-0 right-0 p-4">
               <Badge className="bg-primary text-primary-foreground font-bold">ECONOMIA</Badge>
            </div>
            <CardHeader>
              <CardTitle className="text-2xl font-bold pr-20">PL 1234/2024 - Reforma Tributária Administrativa</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-muted-foreground leading-relaxed">
                Nossa IA identificou uma sobreposição de cargos que, se ajustada conforme a emenda 04, pode gerar uma economia direta de <span className="text-primary font-bold">R$ 450.000,00</span> anuais.
              </p>
              <div className="flex items-center justify-between pt-4 border-t border-border">
                <div className="flex items-center gap-4 text-sm font-bold">
                  <span className="flex items-center gap-1 text-primary"><ShieldCheck className="w-4 h-4" /> Gemini Analysis</span>
                  <span className="text-muted-foreground">Confiança: 98%</span>
                </div>
                <Button variant="link" className="text-primary font-bold flex items-center gap-1">
                  Ver Detalhes <ArrowUpRight className="w-4 h-4" />
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="relative aspect-video glass rounded-3xl flex items-center justify-center overflow-hidden">
           <div className="absolute inset-0 bg-gradient-to-br from-primary/10 to-transparent" />
           <p className="text-muted-foreground font-medium animate-pulse">Visualização de Gastos (Gráfico em breve)</p>
        </div>
      </div>
    </main>
  );
}
