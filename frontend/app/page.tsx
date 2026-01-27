import { ArrowUpRight, TrendingUp, AlertTriangle, ShieldCheck } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { fetchAPI, endpoints } from "@/lib/api";
import Link from "next/link";

async function getStats() {
  try {
    return await fetchAPI(endpoints.stats);
  } catch (error) {
    console.error("Failed to fetch statistics:", error);
    return null;
  }
}

async function getFeaturedProposicao() {
  try {
    const proposicoes = await fetchAPI(`${endpoints.proposicoes}?limit=1`);
    return proposicoes[0] || null;
  } catch (error) {
    console.error("Failed to fetch proposições:", error);
    return null;
  }
}

export default async function Home() {
  const stats = await getStats();
  const featured = await getFeaturedProposicao();

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
          <Link href="/deputados">
            <Button size="lg" className="rounded-full px-8 h-14 text-lg font-bold shadow-xl shadow-emerald-500/20">
              Explorar Deputados
            </Button>
          </Link>
          <Link href="/proposicoes">
            <Button size="lg" variant="outline" className="rounded-full px-8 h-14 text-lg font-bold glass">
              Ver Proposições
            </Button>
          </Link>
        </div>
      </section>

      {/* Highlights Grid */}
      <div className="grid md:grid-cols-3 gap-6">
        <Card className="glass group cursor-pointer hover:border-primary/50 transition-all duration-300">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-bold uppercase tracking-wider text-muted-foreground">Gastos Totais</CardTitle>
            <div className="p-2 rounded-lg bg-emerald-500/10 text-primary">
              <TrendingUp className="h-5 w-5" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-black font-heading tabular-nums">
              {stats ? `R$ ${(stats.total_gastos / 1000000).toFixed(1)}M` : "---"}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Volume total processado pela plataforma
            </p>
          </CardContent>
        </Card>

        <Card className="glass group cursor-pointer hover:border-red-500/50 transition-all duration-300">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-bold uppercase tracking-wider text-muted-foreground">Proposições Analisadas</CardTitle>
            <div className="p-2 rounded-lg bg-red-500/10 text-red-500">
              <AlertTriangle className="h-5 w-5" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-black font-heading tabular-nums">
              {stats?.total_proposicoes || "---"}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Projetos monitorados em tempo real
            </p>
          </CardContent>
        </Card>

        <Card className="glass group cursor-pointer hover:border-blue-500/50 transition-all duration-300">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-bold uppercase tracking-wider text-muted-foreground">Deputados Ativos</CardTitle>
            <div className="p-2 rounded-lg bg-blue-500/10 text-blue-500">
              <ShieldCheck className="h-5 w-5" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-black font-heading tabular-nums">
              {stats?.total_politicos || "---"}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Representantes com dados consolidados
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Featured Insight Section */}
      <div className="grid lg:grid-cols-2 gap-8 items-center pt-8">
        <div className="space-y-6">
          <h2 className="text-4xl font-heading font-black leading-none">
            Última Análise
          </h2>
          {featured ? (
            <Card className="glass border-emerald-500/20 relative overflow-hidden group">
              <div className="absolute top-0 right-0 p-4">
                 <Badge className="bg-primary text-primary-foreground font-bold">RECENTE</Badge>
              </div>
              <CardHeader>
                <CardTitle className="text-2xl font-bold pr-20">{featured.sigla_tipo} {featured.numero}/{featured.ano}</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-muted-foreground leading-relaxed line-clamp-3">
                  {featured.ementa}
                </p>
                <div className="flex items-center justify-between pt-4 border-t border-border">
                  <div className="flex items-center gap-4 text-sm font-bold">
                    <span className="flex items-center gap-1 text-primary"><ShieldCheck className="w-4 h-4" /> AI Monitor</span>
                    <span className="text-muted-foreground">Câmara API</span>
                  </div>
                  <Link href={`/proposicoes/${featured.id}`}>
                    <Button variant="link" className="text-primary font-bold flex items-center gap-1">
                      Analisar <ArrowUpRight className="w-4 h-4" />
                    </Button>
                  </Link>
                </div>
              </CardContent>
            </Card>
          ) : (
            <div className="h-48 glass rounded-2xl flex items-center justify-center text-muted-foreground animate-pulse">
              Carregando proposição em destaque...
            </div>
          )}
        </div>

        <div className="relative aspect-video glass rounded-3xl flex items-center justify-center overflow-hidden">
           <div className="absolute inset-0 bg-gradient-to-br from-primary/10 to-transparent" />
           <p className="text-muted-foreground font-medium animate-pulse">Visualização Geográfica (Mapa em breve)</p>
        </div>
      </div>
    </main>
  );
}
